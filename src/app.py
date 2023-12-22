import os
import shutil
from typing import List
import json
from enum import Enum
from concurrent.futures import as_completed, ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, Form, Query
from pathlib import Path
from pydantic import BaseModel

from divide_track_into_chunks import divide_track_into_chunks
from transcribe_audio.transcribe_audio import TranscribeAudioHF
from transcribe_audio.model import TranscriptAudioResponse
from transcript_to_stable_diffusion_prompt.from_trascript_chunks import (
    generate_stable_diffusion_prompts,
)
from segmind.stable_diffusion import stable_diffusion
from segmind.settings import STABLE_DIFFUSION_STYLES
from video_gen.create_video_from_frames import create_video


app = FastAPI()

transcriber = TranscribeAudioHF()

MAX_MODAL_WORKERS = 10


class TranslationLanguage(str, Enum):
    english = "en"
    hindi = "hi"
    original = ""


class TranscriptionRequest(BaseModel):
    audio_path: str
    language: TranslationLanguage = TranslationLanguage.english


class TranscriptionAPIResponse(BaseModel):
    audio_path: str
    transcription: TranscriptAudioResponse


StableDiffStyle = Enum("Style", {style: style for style in STABLE_DIFFUSION_STYLES})


# Write endpoints for generating video from images and audio
@app.post("/generate_video")
async def generate_video(
    project_name: str = Form(...),
):
    try:
        # Check is the project exists
        project_path = Path("./Projects") / project_name
        if not project_path.exists():
            return {"error": f"Project {project_name} does not exist"}

        # Check if the images folder exists
        images_folder_path = Path("./Projects") / project_name / "images"
        if not images_folder_path.exists():
            return {"error": f"Images folder does not exist for project {project_name}"}

        # Check if the audio folder exists
        audio_folder_path = Path("./Projects") / project_name / "original"
        if not audio_folder_path.exists():
            return {"error": f"Audio folder does not exist for project {project_name}"}

        # Check if the video folder exists
        video_folder_path = Path("./Projects") / project_name / "video"
        if not video_folder_path.exists():
            video_folder_path.mkdir(parents=True, exist_ok=True)

        from datetime import datetime

        video_file_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        save_video_path = os.path.join(video_folder_path, f"{video_file_name}.mp4")

        # Get the only audio file in the audio folder
        audio_file_path = [
            audio_file_path
            for audio_file_path in audio_folder_path.iterdir()
            if audio_file_path.suffix in [".wav", ".mp3"]
        ][0]

        # Call the function to generate the video
        create_video(images_folder_path, audio_file_path, save_video_path)

    except Exception as e:
        return {"error": str(e)}


@app.post("/stable_diffusion")
async def run_stable_diffusion(
    project_name: str = Form(...), style: StableDiffStyle = Query(...)
):
    """
    Run the stable diffusion process for a given project's prompts.

    This function accepts a project name and a style, and runs the stable diffusion process
    for all .txt files in the 'Projects/project_name/stable_diffusion_prompts' directory.

    If the project or the prompts folder does not exist, it returns an error message.

    Args:
        project_name (str): The name of the project.
        style (str): The style to be used in the stable diffusion process.

    Returns:
        dict: A dictionary with a message indicating the stable diffusion process is complete. If any errors occur
        during the process, they are included in the dictionary.
    """
    try:
        # check if the project exists
        project_path = Path("./Projects") / project_name
        if not project_path.exists():
            return {"error": f"Project {project_name} does not exist"}

        # Check if the prompts_folder_path is present
        prompts_folder_path = (
            Path("./Projects") / project_name / "stable_diffusion_prompts"
        )
        if not prompts_folder_path.exists():
            return {
                "error": f"Prompts folder does not exist for project {project_name}"
            }

        # Check if the images_folder_path is present
        images_folder_path = Path("./Projects") / project_name / "images"
        if not images_folder_path.exists():
            # Create the images folder
            images_folder_path.mkdir(parents=True, exist_ok=True)

        # read prompts from prompts_folder_path
        prompts = {}
        for prompt_path in prompts_folder_path.iterdir():
            # Check if the file is a txt file
            if prompt_path.suffix != ".txt":
                continue
            with open(prompt_path, "r") as f:
                save_image_path = os.path.join(
                    images_folder_path, f"{prompt_path.stem}.png"
                )
                prompts[prompt_path.stem] = (f.read(), save_image_path, style)

        def run_stable_diffusion(prompt, save_image_path, style):
            try:
                stable_diffusion(prompt, save_image_path, style.value)
                return True, None
            except Exception as e:
                return False, str(e)

        with ThreadPoolExecutor() as executor:
            future_to_prompt = {
                executor.submit(run_stable_diffusion, *prompt_values): prompt_key
                for prompt_key, prompt_values in prompts.items()
            }
            errors = {}
            for future in as_completed(future_to_prompt):
                prompt_key = future_to_prompt[future]
                success, result = future.result()
                if not success:
                    errors[prompt_key] = result
                else:
                    print("Success : ", prompt_key)
            if len(errors) > 0:
                raise Exception(errors)
    except Exception as e:
        return {"error": str(e)}


@app.post("/generate_prompts")
async def generate_prompts(project_name: str = Form(...)):
    """
    Generate stable diffusion prompts for a given project's transcriptions.

    This function accepts a project name, and generates prompts for all .json files in the
    'Projects/project_name/transcriptions' directory. It saves each prompt as a .txt file
    in the 'Projects/project_name/stable_diffusion_prompts' directory, with the filename
    corresponding to the chunk index.

    If the transcriptions folder does not exist, it returns an error message. If the prompts
    folder does not exist, it creates it.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict: A dictionary with a message indicating the prompts generation is complete. If any errors occur
        during the prompts generation process, they are included in the dictionary.
    """
    try:
        # Check if transcriptions folder exists
        transcriptions_folder_path = (
            Path("./Projects") / project_name / "transcriptions"
        )
        if not transcriptions_folder_path.exists():
            return {
                "error": f"Transcriptions folder does not exist for project {project_name}"
            }
        # Check if prompts folder exists
        prompts_folder_path = (
            Path("./Projects") / project_name / "stable_diffusion_prompts"
        )
        if not prompts_folder_path.exists():
            prompts_folder_path.mkdir(parents=True, exist_ok=True)

        print("Generating prompts...")
        chunks_prompt_dict = generate_stable_diffusion_prompts(
            transcriptions_folder_path
        )

        # Save the indivisual prompts to a .txt file based on their key
        for key in chunks_prompt_dict:
            prompt_save_path = os.path.join(prompts_folder_path, f"chunk_{key}.txt")
            with open(prompt_save_path, "w") as f:
                f.write(chunks_prompt_dict[key])
        return {"message": "Prompts generation complete."}
    except Exception as e:
        return {"error": str(e)}


@app.post("/transcribe_audio_chunks")
async def transcribe_audio_chunks(
    project_name: str = Form(...),
    translation_language: TranslationLanguage = Query(
        default=TranslationLanguage.original,
    ),
):
    """
    Transcribe audio chunks from a given project's audio chunks folder.

    This function accepts a project name, and transcribes all .wav or .mp3 files in the
    'Projects/project_name/audio_chunks' directory. It saves the transcriptions as .json files
    in the 'Projects/project_name/transcriptions' directory.

    If the audio chunks folder does not exist, it returns an error message. If the transcriptions
    folder does not exist, it creates it.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict: A dictionary with a message indicating the transcription is complete. If any errors occur
        during the transcription process, they are included in the dictionary.
    """
    try:
        # Check if audio chunks folder exists
        audio_chunks_folder_path = Path("./Projects") / project_name / "audio_chunks"
        if not audio_chunks_folder_path.exists():
            return {
                "error": f"Audio chunks folder does not exist for project {project_name}"
            }
        # Check if transcription folder exists
        transcription_folder_path = Path("./Projects") / project_name / "transcriptions"
        if not transcription_folder_path.exists():
            transcription_folder_path.mkdir(parents=True, exist_ok=True)

        # Iterate over all audio chunks to trascript them
        audio_files = []
        for audio_chunk_path in audio_chunks_folder_path.iterdir():
            # Check if the file is a WAV file or mp3 file
            if audio_chunk_path.suffix not in [".wav", ".mp3"]:
                continue

            audio_files.append(audio_chunk_path)

        def transcribe_audio_and_save(audio_chunk_path: str):
            try:
                # Transcribe the audio chunk
                if translation_language == TranslationLanguage.english:
                    transcription = transcriber.transcribe_audio_to_eng(
                        audio_chunk_path,
                    )
                elif translation_language == TranslationLanguage.hindi:
                    transcription = transcriber.transcribe_audio(
                        audio_chunk_path,
                    )
                else:
                    return False, Exception(
                        "Invalid language : {translation_language}}"
                    )
                return True, transcription
            except Exception as e:
                return False, e

        # Use a ThreadPoolExecutor to transcribe the audio files in parallel
        with ThreadPoolExecutor(max_workers=MAX_MODAL_WORKERS) as executor:
            future_to_file = {
                executor.submit(transcribe_audio_and_save, file): file
                for file in audio_files
            }
            failures = {}
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                success, result = future.result()
                if success:
                    # Save the transcription to a .json file
                    transcript_save_path = os.path.join(
                        transcription_folder_path, f"{Path(file).stem}.json"
                    )
                    with open(transcript_save_path, "w") as f:
                        json.dump(result, f)
                else:
                    failures[file] = result
            # If there are any failures, raise an exception
            if len(failures) > 0:
                raise Exception(failures)

            return {"message": "Transcription complete."}
    except Exception as e:
        return {"error": str(e)}


@app.post("/transcribe_audio", response_model=TranscriptionAPIResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe audio from a given audio file path.

    This function accepts a request containing an audio file path and an optional language.
    If the language is English or not provided, it uses the `transcribe_audio_to_eng` method.
    If the language is not supported, it returns an error message.

    Args:
        request (TranscriptionRequest): A request object containing the audio file path and an optional language.

    Returns:
        TranscriptionAPIResponse: A response object containing the audio file path and the transcription.
        If the language is not supported, the transcription will be empty and an error message will be included.
    """
    try:
        if request.language in ["en", "english"]:
            transcription = transcriber.transcribe_audio_to_eng(request.audio_path)
        elif request.language == "":
            transcription = transcriber.transcribe_audio(request.audio_path)
        else:
            return {"error": f"Invalid language : {request.language}"}
        return TranscriptionAPIResponse(
            audio_path=request.audio_path, transcription=transcription
        )
    except Exception as e:
        return {"error": str(e)}


@app.post("/get_chunks/")
async def get_chunks(
    file: UploadFile = File(...), bpm: int = Form(...), project_name: str = Form(...)
):
    """
    This function receives an audio file, a BPM value, and a project name. It saves the audio file in the
    'Projects/project_name/original' directory, divides the audio file into chunks based on the BPM value,
    and saves the chunks in the 'Projects/project_name/audio_chunks' directory.

    Parameters:
    file (UploadFile): The audio file to be divided into chunks.
    bpm (int): The BPM value to be used to divide the audio file.
    project_name (str): The name of the project.

    Returns:
    dict: A dictionary with a message and the path to the chunks folder.
    """

    try:
        # Set the path where the original file will be saved
        original_save_folder_path = Path("./Projects") / project_name / "original"
        original_save_folder_path.mkdir(parents=True, exist_ok=True)

        # Save the uploaded file to the new path
        file_path = original_save_folder_path / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Set the path where chunks will be saved
        chunk_save_folder_path = Path("./Projects") / project_name / "audio_chunks"
        chunk_save_folder_path.mkdir(parents=True, exist_ok=True)

        # Call the function to divide the track
        divide_track_into_chunks(file_path, bpm, str(chunk_save_folder_path))

        return {
            "message": "Audio file processed and chunks saved.",
            "chunks_folder": str(chunk_save_folder_path),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
