import os
import subprocess

from moviepy.editor import ImageClip, concatenate_videoclips
from moviepy.editor import ImageSequenceClip, AudioFileClip

from llm.gpt import GPT3Chat
from segmind.stable_diffusion import stable_diffusion
from video_gen.utils import split_srt_chunk


def generate_images_from_srt(
    srt_file_path: str,
    save_images_folder_path: str,
):
    # Check if the folder path exists
    if not os.path.exists(save_images_folder_path):
        raise Exception(f"Folder {save_images_folder_path} does not exist")

    # Read srt file with lyrics
    with open(srt_file_path, "r") as file:
        srt_text = file.read()

    # Split the file into chunks
    chunks = srt_text.strip().split("\n\n")

    # Get GPT agent
    context = """
    You are a expert in story telling through images who can analyze lyrics of a rap song and represent them in clear, concise words.
    """
    # NOTE: We are using `gpt-3.5-turbo-16k` as without it after a few bars It would have exceeded the token limit
    # TODO: Whatever model we choose, there is a possibility that it may exceed the prompt size so we need to handle it gracefully. At the tope of my head we can do: 1. Summarize the lyrics and use the story narrated until now as history. 2. Just keep deleting the earliest history. 3. Start with a smaller model and when it reaches the limit use model with  bigger context size (not sure if it will work).
    gpt_agent = GPT3Chat("gpt-3.5-turbo-16k", context)
    for _, chunk in enumerate(chunks):
        index, _, subtitle_text = split_srt_chunk(chunk)

        # NOTE: As of now when there is no lyrics we are replacing that with keyword, `Music`. We need to handle this properly.
        if subtitle_text.strip() == "Music":
            # promt = """
            # Describe in clear and concise words the image that would represent dicision paralysis.
            # """
            # response = gpt_agent.get_response(promt)
            # print(response)
            # stable_diffusion(
            #     response,
            #     os.path.join(
            #         save_images_folder_path,
            #         f"{index}.png",
            #     ),
            #     "anime",
            # )
            continue

        promt = f"""
        You are tasked to represent each line of the rap track in a single image. Describe in clear concise words what this image should entail. You should use context from previous lyrics to build a enthralling story. 
        Lyrics:
        {subtitle_text}
        """
        response = gpt_agent.get_response(promt)
        print(response)
        stable_diffusion(
            response,
            os.path.join(
                save_images_folder_path,
                f"{index}.png",
            ),
            "anime",
        )

        print("*" * 50)


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


"""
image_folder_path = "results/results_3_5_turbo_16k/"
audio_file_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111.wav"
srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
save_video_path = (
    "results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff.mp4"
)
save_video_path_with_audio = "results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff_with_context_audio.mp4"
create_video(
    image_folder_path,
    audio_file_path,
    save_video_path,
    save_video_path_with_audio,
)
"""
# """
srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
context_srt_file_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation_context.srt"
save_images_folder_path = "/Users/neeraj/Work/generative_rap_video/src/results/results_3_5_turbo_16k_w_o_context_base_model/"
generate_images_from_srt(
    srt_path,
    # context_srt_file_path,
    save_images_folder_path,
)
# """
"""
ffmpeg -i results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff.mp4 -i ../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111.wav -c:v copy -c:a aac -strict experimental results/video/karna_kya_hai_tujhe_bpm_111_gpt_3_5_16_k_stable_diff_ffmpeg.mp4
"""
