import os

from transcribe_audio.model import TranscriptAudioResponse
from video_gen.srt_to_images.srt_to_stable_diffusion_prompt import (
    chunks_to_stable_diffusion_prompt,
)


def generate_stable_diffusion_prompts(transcript_chunks_folder_path: str):
    # Check if the folder path exists
    if not os.path.exists(transcript_chunks_folder_path):
        raise Exception(f"Folder {transcript_chunks_folder_path} does not exist")

    # Iterate over all transcript chunks
    transcript_chunk = []
    transcript_chunk_text_index = []
    for transcript_chunk_path in os.listdir(transcript_chunks_folder_path):
        # Check if the file is a json file
        if not transcript_chunk_path.endswith(".json"):
            continue

        # Get the index of the transcript chunk the name format is chunk_{index}.json
        index = int(transcript_chunk_path.split("_")[1].split(".")[0])

        # Read the transcript chunk
        with open(
            os.path.join(transcript_chunks_folder_path, transcript_chunk_path), "r"
        ) as f:
            transcript_chunk = TranscriptAudioResponse(f.read())

        transcript_chunk.append(transcript_chunk)
        transcript_chunk_text_index.append(index)

    # Sort transcript_chunk based on transcript_chunk_text_index in ascending order
    transcript_chunk = [
        transcript_chunk
        for _, transcript_chunk in sorted(
            zip(transcript_chunk_text_index, transcript_chunk)
        )
    ]

    sd_prompt_for_transcript_chunk = chunks_to_stable_diffusion_prompt(transcript_chunk)
