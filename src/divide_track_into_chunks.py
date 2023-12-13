import argparse
import os

import librosa
import soundfile as sf


def divide_track_into_chunks(
    audio_track_path: str,
    bpm: int,
    chunk_save_folder_path: str,
):
    """
    Divides an audio track into equal-length chunks based on the track's BPM (Beats Per Minute).

    This function loads an audio track from the specified path, calculates the duration of one bar
    (four beats) based on the given BPM, and then divides the track into chunks of one bar each.
    These chunks are saved as separate audio files in the specified folder.

    Parameters:
    audio_track_path (str): Path to the audio track file.
    bpm (int): The BPM of the audio track, used to determine the length of each chunk.
    chunk_save_folder_path (str): Path to the folder where the audio chunks will be saved.
                                  The folder is created if it does not exist.

    Each chunk is saved as a WAV file with a filename indicating its sequence in the original track,
    such as 'chunk_1.wav', 'chunk_2.wav', etc.

    Dependencies:
    - librosa: for loading and processing the audio file.
    - os: for folder creation and path manipulation.
    - soundfile (sf): for saving the audio chunks.

    Note:
    The function assumes a 4/4 time signature, meaning each bar consists of four beats.
    """
    # Load audio file
    y, sr = librosa.load(audio_track_path)

    # Calculate the duration of 1 beat in seconds
    beat_duration = 60 / bpm

    # Calculate the duration of 1 bar (4 beats) in seconds
    bar_duration = beat_duration * 4

    # Calculate the number of samples in 1 bar
    samples_per_bar = int(bar_duration * sr)

    # Divide the audio file into chunks of 1 bar
    audio_chunks = [
        y[i : i + samples_per_bar] for i in range(0, len(y), samples_per_bar)
    ]

    # Create the save directory if it doesn't exist
    if not os.path.exists(chunk_save_folder_path):
        os.makedirs(chunk_save_folder_path)

    # Save each audio chunk with a sequence number
    for i, chunk in enumerate(audio_chunks):
        output_file = os.path.join(chunk_save_folder_path, f"chunk_{i+1}.wav")
        sf.write(output_file, chunk, sr)


if __name__ == "__main__":
    # Set up argparse
    parser = argparse.ArgumentParser(
        description="Divide an audio file into chunks of 1 bar (4 beats)."
    )
    parser.add_argument("file_path", type=str, help="Path to the audio file.")
    parser.add_argument(
        "bpm", type=int, help="Beats per minute (BPM) of the audio file."
    )
    parser.add_argument("save_path", type=str, help="Path to save the audio chunks.")

    # Parse the arguments
    args = parser.parse_args()

    divide_track_into_chunks(
        args.file_path,
        args.bpm,
        args.save_path,
    )
