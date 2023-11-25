import json
import os
import re
import argparse
from typing import List


def create_srt_and_json_files(
    results: List, bpm: int, save_path: str, filename: str = "output"
):
    """
    Create SRT and JSON files from the provided results.

    Args:
        results (list): A list of dictionaries containing the transcribed results.
            The list should be sorted in the desired sequence as we are merging sequential information.
        bpm (float): The beats per minute (BPM) value used to calculate the duration of each chunk.
        save_path (str): The path to save the output JSON and SRT files.

    Returns:
        None

    Raises:
        None
    """
    # Calculate the start and end times for each chunk
    start_time = 0
    for result in results:
        chunk = result["chunks"][0]
        text = chunk["text"]
        duration = (60 / bpm) * 4
        # duration = chunk["timestamp"][1] - chunk["timestamp"][0]
        end_time = start_time + duration
        result["start_time"] = start_time
        result["end_time"] = end_time
        start_time = end_time

    # Create the output JSON file
    output_json_file = os.path.join(save_path, f"{filename}.json")
    with open(output_json_file, "w") as f:
        json.dump(results, f, indent=4)

    # Create the output SRT file
    output_srt_file = os.path.join(save_path, f"{filename}.srt")
    with open(output_srt_file, "w") as f:
        for i, result in enumerate(results):
            start_time = result["start_time"]
            end_time = result["end_time"]
            transcript = result["text"]
            srt = f"{i+1}\n{start_time:.2f} --> {end_time:.2f}\n{transcript}\n\n"
            f.write(srt)


if __name__ == "__main__":
    # Set up argparse
    parser = argparse.ArgumentParser(
        description="Divide an audio file into chunks of 1 bar (4 beats)."
    )
    parser.add_argument(
        "translation_json_folder_path",
        type=str,
        help="Path to save the audio chunks respective translation.",
    )
    parser.add_argument(
        "bpm", type=int, help="Beats per minute (BPM) of the audio file."
    )
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
