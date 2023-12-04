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
