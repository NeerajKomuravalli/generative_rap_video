import json
import os
import re
import argparse

# Set up argparse
parser = argparse.ArgumentParser(
    description="Divide an audio file into chunks of 1 bar (4 beats)."
)
parser.add_argument(
    "translation_json_folder_path",
    type=str,
    help="Path to save the audio chunks respective translation.",
)
parser.add_argument("bpm", type=int, help="Beats per minute (BPM) of the audio file.")
parser.add_argument("save_path", type=str, help="Path to save the audio chunks.")

# Parse the arguments
args = parser.parse_args()

# Load the JSON files and concatenate the results
results = []
seq = []
for filename in os.listdir(args.translation_json_folder_path):
    if filename.endswith(".json"):
        seq.append(int(re.findall(r"\d+", filename)[0]))
        json_file = os.path.join(args.translation_json_folder_path, filename)
        with open(json_file, "r") as f:
            result = json.load(f)
            results.append(result)

# Sort the results by seq list
results = [x for _, x in sorted(zip(seq, results))]

# Calculate the start and end times for each chunk
start_time = 0
for result in results:
    chunk = result["chunks"][0]
    text = chunk["text"]
    duration = (60 / args.bpm) * 4
    # duration = chunk["timestamp"][1] - chunk["timestamp"][0]
    end_time = start_time + duration
    result["start_time"] = start_time
    result["end_time"] = end_time
    start_time = end_time

# Create the output JSON file
output_json_file = os.path.join(args.save_path, "output.json")
with open(output_json_file, "w") as f:
    json.dump(results, f, indent=4)

# Create the output SRT file
output_srt_file = os.path.join(args.save_path, "output.srt")
with open(output_srt_file, "w") as f:
    for i, result in enumerate(results):
        start_time = result["start_time"]
        end_time = result["end_time"]
        transcript = result["text"]
        srt = f"{i+1}\n{start_time:.2f} --> {end_time:.2f}\n{transcript}\n\n"
        f.write(srt)
