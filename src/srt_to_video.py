import os
from concurrent.futures import ThreadPoolExecutor

from llm.gpt import GPT3Chat
from segmind.stable_diffusion import stable_diffusion


def parse_srt(srt_file_path: str, save_images_folder_path: str):
    # Check if the folder path exists
    if not os.path.exists(save_images_folder_path):
        raise Exception(f"Folder {save_images_folder_path} does not exist")

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
    for chunk in chunks:
        # Split the chunk into lines
        lines = chunk.split("\n")

        # NOTE: May be this is a not a great check but works for a POC. Come back to it later when it's needed
        if len(lines) < 3:
            raise Exception("Corrupted file")

        # The first line is the index
        index = lines[0]

        # The second line is the time range
        time_range = lines[1]

        # The remaining lines are the subtitle text
        subtitle_text = "\n".join(lines[2:])

        if subtitle_text.strip() == "Music":
            continue
        print(subtitle_text)
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


srt_path = "../data/original/karna_kya_hai_tujhe/karna_kya_hai_tujhe_bpm_111_english_translation.srt"
save_images_folder_path = (
    "/Users/neeraj/Work/generative_rap_video/src/results/results_3_5_turbo_16k/"
)
parse_srt(
    srt_path,
    save_images_folder_path,
)
