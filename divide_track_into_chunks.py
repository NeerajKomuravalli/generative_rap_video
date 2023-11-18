import argparse
import os

import librosa
import soundfile as sf

# Set up argparse
parser = argparse.ArgumentParser(
    description="Divide an audio file into chunks of 1 bar (4 beats)."
)
parser.add_argument("file_path", type=str, help="Path to the audio file.")
parser.add_argument("bpm", type=int, help="Beats per minute (BPM) of the audio file.")
parser.add_argument("save_path", type=str, help="Path to save the audio chunks.")

# Parse the arguments
args = parser.parse_args()

# Load audio file
y, sr = librosa.load(args.file_path)

# Set the BPM of your audio file
bpm = args.bpm

# Calculate the duration of 1 beat in seconds
beat_duration = 60 / bpm

# Calculate the duration of 1 bar (4 beats) in seconds
bar_duration = beat_duration * 4

# Calculate the number of samples in 1 bar
samples_per_bar = int(bar_duration * sr)

# Divide the audio file into chunks of 1 bar
audio_chunks = [y[i : i + samples_per_bar] for i in range(0, len(y), samples_per_bar)]

# Create the save directory if it doesn't exist
if not os.path.exists(args.save_path):
    os.makedirs(args.save_path)

# Save each audio chunk with a sequence number
for i, chunk in enumerate(audio_chunks):
    output_file = os.path.join(args.save_path, f"chunk_{i+1}.wav")
    sf.write(output_file, chunk, sr)
