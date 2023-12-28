import os
import shutil
from datetime import datetime
from typing import Dict
import json
from enum import Enum
from concurrent.futures import as_completed, ThreadPoolExecutor
import base64

from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Body
from fastapi.responses import FileResponse
from pathlib import Path

from divide_track_into_chunks import divide_track_into_chunks
from transcribe_audio.transcribe_audio import TranscribeAudioHF
from transcript_to_stable_diffusion_prompt.from_trascript_chunks import (
    generate_stable_diffusion_prompts,
)
from segmind.stable_diffusion import stable_diffusion
from segmind.settings import STABLE_DIFFUSION_STYLES
from video_gen.create_video_from_frames import create_video
from fastapi_models import (
    TranslationLanguage,
    TranscriptionRequest,
    TranscriptionAPIResponse,
)

app = FastAPI()

transcriber = TranscribeAudioHF()

MAX_MODAL_WORKERS = 10


StableDiffStyle = Enum("Style", {style: style for style in STABLE_DIFFUSION_STYLES})


class UpdatePromptRequest(BaseModel):
    updated_sd_prompt: str


@app.post("/create_project/{project_name}")
async def create_project(project_name: str):
    try:
        # Define the path to the Projects folder
        projects_folder_path = Path("./Projects")

        # Create the Projects folder if it does not exist
        projects_folder_path.mkdir(exist_ok=True)

        # Define the path to the project's folder
        project_folder_path = projects_folder_path / project_name

        # NOTE: For sake of simplicity not returning with different status when the project exists. Handle it later if needed
        if not project_folder_path.exists():
            # Create the project's folder
            project_folder_path.mkdir()

        return {
            "success": True,
            "message": f"Project {project_name} has been created successfully",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


class ProjectStatus(BaseModel):
    project: bool
    original: bool
    audio_chunks: int
    transcriptions: int
    prompt: int
    images: int
    video: int


@app.get("/project_status/{project_name}")
async def project_status(project_name: str):
    try:
        # Define the path to the project's folder
        project_folder_path = Path("./Projects") / project_name

        status = ProjectStatus(
            project=False,
            original=False,
            audio_chunks=0,
            transcriptions=0,
            prompt=0,
            images=0,
            video=False,
        )
        # Check if the project's folder exists
        if not project_folder_path.exists():
            return {
                "success": True,
                "status": status,
            }
        else:
            status.project = True

        original = Path("./Projects") / project_name / "original"
        if (not original.exists()) or (
            len([f for f in original.glob("*") if f.name != ".DS_Store"]) > 0
        ):
            return {
                "success": True,
                "status": status,
            }
        else:
            status.original = True

        # First we will check for
        audio_chunks_folder_path = project_folder_path / "audio_chunks"
        # Check if the audio chunks folder exists
        if not audio_chunks_folder_path.exists():
            return {
                "success": True,
                "status": status,
            }
        else:
            status.audio_chunks = len(
                list(audio_chunks_folder_path.glob("*.mp3"))
                + list(audio_chunks_folder_path.glob("*.wav"))
            )

        transcriptions_folder_path = project_folder_path / "transcriptions"
        if not transcriptions_folder_path.exists():
            return {
                "success": True,
                "status": status,
            }
        else:
            status.transcriptions = len(list(transcriptions_folder_path.glob("*.json")))

        # Check if the transcriptions folder exists
        stable_diffusion_prompts_folder_path = (
            project_folder_path / "stable_diffusion_prompts"
        )
        if not stable_diffusion_prompts_folder_path.exists():
            return {
                "success": True,
                "status": status,
            }
        else:
            status.prompt = len(
                list(stable_diffusion_prompts_folder_path.glob("*.txt"))
            )

        images_folder_path = project_folder_path / "images"
        # Check if the images folder exists
        if not images_folder_path.exists():
            return {
                "success": True,
                "status": status,
            }
        else:
            status.images = len(
                list(images_folder_path.glob("*.jpg"))
                + list(images_folder_path.glob("*.png"))
            )

        video_folder_path = project_folder_path / "video"
        if not video_folder_path.exists():
            return {
                "success": True,
                "status": status,
            }
        else:
            status.video = len(list(video_folder_path.glob("*.mp4")))

        return {
            "success": True,
            "status": status,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.get("/get_audio_chunks/")
async def get_audio_chunks(project_name: str):
    try:
        # Define the path to the project's audio folder
        audio_folder_path = Path("./Projects") / project_name / "audio_chunks"

        # Check if the audio folder exists
        if not audio_folder_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Audio folder does not exist for project {project_name}",
            )

        # Get the paths of all the audio chunks
        audio_chunks_paths = [
            str(chunk_path)
            for ext in ["*.wav", "*.mp3"]
            for chunk_path in audio_folder_path.glob(ext)
        ]

        return {
            "success": True,
            "audio_chunks": audio_chunks_paths,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.get("/get_sd_prompts/{project_name}/")
async def get_sd_prompts(project_name: str):
    try:
        # Define the path to the project's transcriptions folder
        sd_prompts_folder_path = (
            Path("./Projects") / project_name / "stable_diffusion_prompts"
        )

        # Check if the transcriptions folder exists
        if not sd_prompts_folder_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcriptions folder does not exist for project {project_name}",
            )

        # Get the paths of all the transcription files
        sd_prompts_paths = [
            str(prompt_path) for prompt_path in sd_prompts_folder_path.glob("*.txt")
        ]

        return {
            "success": True,
            "prompts": sd_prompts_paths,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/get_sd_prompt/{project_name}/{chunk_name}")
async def get_sd_prompt(project_name: str, chunk_name: str):
    try:
        # Define the path to the prompt file
        promopt_file_path = (
            Path("./Projects")
            / project_name
            / "stable_diffusion_prompts"
            / f"{chunk_name}.txt"
        )

        # Check if the transcription file exists
        if not promopt_file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcription file {chunk_name} does not exist for project {project_name}",
            )

        # Read the transcription file
        with open(promopt_file_path, "r") as file:
            # load json file
            prompt = file.read()

        return {
            "success": True,
            "prompt": prompt,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.get("/get_transcript/{project_name}/{transcript_name}")
async def get_transcript(project_name: str, transcript_name: str):
    try:
        # Define the path to the transcription file
        transcription_file_path = (
            Path("./Projects")
            / project_name
            / "transcriptions"
            / f"{transcript_name}.json"
        )

        # Check if the transcription file exists
        if not transcription_file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcription file {transcript_name} does not exist for project {project_name}",
            )

        # Read the transcription file
        with open(transcription_file_path, "r") as file:
            # load json file
            transcription = json.load(file)

        return {
            "success": True,
            "transcription": transcription,
        }
    except Exception as e:
        return {
            "seccess": False,
            "error": str(e),
        }


@app.get("/get_audio_chunk/{project_name}/{chunk_name}")
async def get_audio_chunk(project_name: str, chunk_name: str):
    try:
        # Define the path to the audio chunk
        audio_chunk_path = (
            Path("./Projects") / project_name / "audio_chunks" / f"{chunk_name}.wav"
        )

        # Check if the audio chunk exists
        if not audio_chunk_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Audio chunk {chunk_name} does not exist for project {project_name}",
            )

        with open(audio_chunk_path, "rb") as audio_file:
            # Return the audio chunk as a file response
            return {
                "success": True,
                "audio": base64.b64encode(audio_file.read()).decode("utf-8"),
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.get("/get_transcriptions/{project_name}")
async def get_transcriptions(project_name: str):
    try:
        # Define the path to the project's transcriptions folder
        transcriptions_folder_path = (
            Path("./Projects") / project_name / "transcriptions"
        )

        # Check if the transcriptions folder exists
        if not transcriptions_folder_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcriptions folder does not exist for project {project_name}",
            )

        # Get the paths of all the transcription files
        transcriptions_paths = [
            str(transcription_path)
            for transcription_path in transcriptions_folder_path.glob("*.txt")
        ]

        return {
            "success": True,
            "transcriptions": transcriptions_paths,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/update_sd_prompt/{project_name}/{file_name}")
async def update_sd_prompt(
    project_name: str,
    file_name: str,
    updated_sd_prompt: UpdatePromptRequest = Body(...),
):
    try:
        # Define the path to the transcription file
        prompt_file_path = (
            Path("./Projects")
            / project_name
            / "stable_diffusion_prompts"
            / f"{file_name}.txt"
        )

        # Check if the transcription file exists
        if not prompt_file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcription file {file_name} does not exist for project {project_name}",
            )

        # Update the transcription file
        with open(prompt_file_path, "w") as file:
            file.write(updated_sd_prompt.updated_sd_prompt)

        return {
            "success": True,
            "message": f"Prompt file {file_name} for project {project_name} has been updated successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/update_transcription/{project_name}/{file_name}")
async def update_transcription(
    project_name: str, file_name: str, updated_transcription: Dict = Body(...)
):
    try:
        # Define the path to the transcription file
        transcription_file_path = (
            Path("./Projects") / project_name / "transcriptions" / f"{file_name}.json"
        )

        # Check if the transcription file exists
        if not transcription_file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcription file {file_name} does not exist for project {project_name}",
            )

        # Update the transcription file
        with open(transcription_file_path, "w") as file:
            json.dump(updated_transcription, file)

        return {
            "success": True,
            "message": f"Transcription file {file_name} for project {project_name} has been updated successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Write endpoints for generating video from images and audio
@app.post("/generate_video")
async def generate_video(
    project_name: str = Form(...),
):
    try:
        # Check is the project exists
        project_path = Path("./Projects") / project_name
        if not project_path.exists():
            raise Exception(f"Project {project_name} does not exist")

        # Check if the images folder exists
        images_folder_path = Path("./Projects") / project_name / "images"
        if not images_folder_path.exists():
            raise Exception(f"Images folder does not exist for project {project_name}")

        # Check if the audio folder exists
        audio_folder_path = Path("./Projects") / project_name / "original"
        if not audio_folder_path.exists():
            raise Exception(f"Audio folder does not exist for project {project_name}")

        # Check if the video folder exists
        video_folder_path = Path("./Projects") / project_name / "video"
        if not video_folder_path.exists():
            video_folder_path.mkdir(parents=True, exist_ok=True)

        video_file_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        save_video_path = os.path.join(video_folder_path, f"{video_file_name}.mp4")

        # Get the only audio file in the audio folder
        audio_file_path = [
            audio_file_path
            for audio_file_path in audio_folder_path.iterdir()
            if audio_file_path.suffix in [".wav", ".mp3"]
        ][0]

        print("images_folder_path : ", images_folder_path)
        print("audio_file_path : ", audio_file_path)
        print("save_video_path : ", save_video_path)
        # Call the function to generate the video
        create_video(images_folder_path, audio_file_path, save_video_path)

        return {
            "success": True,
            "message": "Video generated successfully.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


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
            raise Exception(f"Project {project_name} does not exist")

        # Check if the prompts_folder_path is present
        prompts_folder_path = (
            Path("./Projects") / project_name / "stable_diffusion_prompts"
        )
        if not prompts_folder_path.exists():
            raise Exception(f"Prompts folder does not exist for project {project_name}")

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

        return {
            "success": True,
            "message": "images generates successfully",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


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
            raise Exception(
                f"Transcriptions folder does not exist for project {project_name}"
            )

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
        return {
            "success": True,
            "message": "Prompts generation complete.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


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
    print("translation_language : ", translation_language)
    try:
        # Check if audio chunks folder exists
        audio_chunks_folder_path = Path("./Projects") / project_name / "audio_chunks"
        if not audio_chunks_folder_path.exists():
            raise Exception(
                f"Audio chunks folder does not exist for project {project_name}"
            )

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
                elif translation_language in [
                    TranslationLanguage.hindi,
                    TranslationLanguage.original,
                ]:
                    transcription = transcriber.transcribe_audio(
                        audio_chunk_path,
                    )
                else:
                    return False, Exception(
                        f"Invalid language : {translation_language}"
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

            return {
                "success": True,
                "message": "Transcription complete.",
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


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
        return {
            "success": True,
            "data": TranscriptionAPIResponse(
                audio_path=request.audio_path, transcription=transcription
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.post("/upload_audio/{project_name}")
async def upload_audio(project_name: str, file: UploadFile = File(...)):
    try:
        # Define the path to the directory where the file will be saved
        file_save_path = Path("./Projects") / project_name / "original"

        # Create the directory if it does not exist
        file_save_path.mkdir(parents=True, exist_ok=True)

        # Make sure no file is present in the directory
        # NOTE: For now we will not allow presence of any file
        if len([f for f in file_save_path.glob("*") if f.name != ".DS_Store"]) > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Audio file already exists in project {project_name}",
            )

        # Define the path to the file
        file_path = file_save_path / file.filename

        # Save the uploaded file to the new path
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "message": f"File {file.filename} has been uploaded successfully to project {project_name}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.post("/get_chunks/{project_name}")
async def get_chunks(project_name: str, bpm: int = Form(...)):
    try:
        # Set the path where the original file will be saved
        original_save_folder_path = Path("./Projects") / project_name / "original"
        if not original_save_folder_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Original folder does not exist for project {project_name}",
            )
        # Get the first audio file in the directory
        audio_files = list(original_save_folder_path.glob("*.mp3")) + list(
            original_save_folder_path.glob("*.wav")
        )
        if not audio_files:
            raise HTTPException(
                status_code=404,
                detail=f"No audio files found in the original folder for project {project_name}",
            )
        elif len(audio_files) > 1:
            raise HTTPException(
                status_code=404,
                detail=f"Multiple audio files found in the original folder for project {project_name}",
            )

        # Use the first audio file
        file_path = audio_files[0]

        # Set the path where chunks will be saved
        chunk_save_folder_path = Path("./Projects") / project_name / "audio_chunks"
        chunk_save_folder_path.mkdir(parents=True, exist_ok=True)

        # Call the function to divide the track
        divide_track_into_chunks(file_path, bpm, str(chunk_save_folder_path))

        return {
            "success": True,
            "message": "Audio file processed and chunks saved.",
            "chunks_folder": str(chunk_save_folder_path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    pass


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
            "success": True,
            "message": "Audio file processed and chunks saved.",
            "chunks_folder": str(chunk_save_folder_path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
