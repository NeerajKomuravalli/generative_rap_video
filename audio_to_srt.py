import json
import time
import argparse
import os

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from merge_translated_json_and_create_srt import create_srt_and_json_files


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

# Set up argparse
parser = argparse.ArgumentParser(
    description="Transcribe audio files using a speech-to-text model."
)
parser.add_argument(
    "audio_path",
    type=str,
    help="Path to the audio file or folder containing audio files.",
)
parser.add_argument("bpm", type=int, help="Beats per minute (BPM) of the audio file.")
parser.add_argument(
    "save_path",
    type=str,
    help="Path to save the srt and json files of translated audio.",
)
parser.add_argument(
    "save_filename", type=str, help="filename to save the srt and json files."
)

args = parser.parse_args()

# Load model
print("Loading model...")
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True,
    local_files_only=True,
)
model.to(device)

# Load processor
print("Loading processor...")
processor = AutoProcessor.from_pretrained(model_id)

# Create pipeline
print("Creating pipeline...")
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

# Transcribe audio files
if os.path.isfile(args.audio_path):
    # Single audio file
    audio_files = [args.audio_path]
else:
    # Folder containing audio files
    audio_files = [
        os.path.join(args.audio_path, file)
        for file in os.listdir(args.audio_path)
        if file.lower().endswith((".wav", ".mp3"))
    ]

# Sort the audio files based on their names. The pattern audio files follow is `chunk_<number>.wav`.
audio_files = sorted(
    audio_files, key=lambda x: int(x.split("/")[-1].split(".")[0].split("_")[-1])
)

results = []
for audio_file in audio_files:
    print(f"Transcribing audio file: {audio_file}")
    result = pipe(
        audio_file,
        generate_kwargs={"language": "hindi"},
        return_timestamps=True,
    )
    results.append(result)

# Use create_srt_and_json_files form merge_translated_json_and_create_srt.py to create the SRT and JSON files.
create_srt_and_json_files(results, args.bpm, args.save_path, args.save_filename)
