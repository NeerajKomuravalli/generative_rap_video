import os
import subprocess

from moviepy.editor import ImageClip, concatenate_videoclips


def create_video(
    image_folder_path: str,
    audio_file_path: str,
    save_video_path: str,
    save_video_path_with_audio: str,
):
    # Get a sorted list of all image file paths
    image_files = sorted(
        [
            os.path.join(image_folder_path, img)
            for img in os.listdir(image_folder_path)
            if img.endswith(".png")
        ],
        key=lambda img: int(img.split("/")[-1].split(".")[0]),
    )

    # NOTE: TODO: Automatic calculation of the image duration. Use librosa to do it
    img_duration = 2.16

    # Create a video clip from each image
    clips = [ImageClip(img).set_duration(img_duration) for img in image_files]

    # Concatenate the clips into a single video clip
    video = concatenate_videoclips(clips)

    # Write the result to a file
    video.write_videofile(
        save_video_path,
        codec="libx264",
        fps=32,
    )

    # Add the audio to the video
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            save_video_path,
            "-i",
            audio_file_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            save_video_path_with_audio,
        ]
    )
