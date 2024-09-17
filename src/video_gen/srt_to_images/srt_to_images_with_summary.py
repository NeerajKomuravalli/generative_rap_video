import os

from llm.gpt import GPT3Chat
from segmind.stable_diffusion import stable_diffusion
from video_gen.utils import split_srt_chunk
from prompt_generator.metrics_mule_prompt_for_images import prompt_with_summary
from prompt_generator.intro_outro_prompt_gen import prompt as intro_outro_prompt


def generate_images(
    srt_file_path: str,
    save_images_folder_path: str,
    models: [str],
):
    # Check if the folder path exists
    if not os.path.exists(save_images_folder_path):
        raise Exception(f"Folder {save_images_folder_path} does not exist")

    # Read srt file with lyrics
    with open(srt_file_path, "r") as file:
        srt_text = file.read()

    # Split the file into chunks
    chunks = srt_text.strip().split("\n\n")

    summary_gpt_agent = GPT3Chat("gpt-3.5-turbo")
    content = ""
    for _, chunk in enumerate(chunks):
        _, _, subtitle_text = split_srt_chunk(chunk)

        if subtitle_text.strip() in ["Music", ""]:
            continue

        content += "\n" + subtitle_text

    prompt = f"""
    You are an expert in summarizing the lyrics of rap music. Below is the english translation of the hindi rap track.
    Below are the lyrics:
    {content}
    Summarize the track
    """

    summary = summary_gpt_agent.get_response(prompt)
    print("Summary : ", summary)
    print("*" * 50)
    # '''
    stable_diff_prompt_gen_agent = GPT3Chat("gpt-3.5-turbo-16k")
    prompt = prompt_with_summary % (summary)
    print(prompt)
    print("*" * 50)
    response = stable_diff_prompt_gen_agent.get_response(prompt)
    print(response)
    print("*" * 50)

    intro_prompt = intro_outro_prompt % (summary, "intro")
    intro_stable_diff_prompt_gen = GPT3Chat("gpt-3.5-turbo")
    intro_stable_diff_prompt_gen.get_response(intro_prompt)

    outro_prompt = intro_outro_prompt % (summary, "outro")
    outro_stable_diff_prompt_gen = GPT3Chat("gpt-3.5-turbo")
    outro_stable_diff_prompt_gen.get_response(outro_prompt)
    for _, chunk in enumerate(chunks):
        index, _, subtitle_text = split_srt_chunk(chunk)
        # NOTE: TODO: The logic to decide if it's intro or outro is not relly scalable and should be changed
        if subtitle_text.strip() in ["Music", ""]:
            if int(index) < len(chunks) / 2:
                response = intro_stable_diff_prompt_gen.get_response("Next")
            else:
                response = outro_stable_diff_prompt_gen.get_response("Next")
        else:
            response = stable_diff_prompt_gen_agent.get_response(subtitle_text)
        print(response)
        # """
        for model in models:
            stable_diffusion(
                response,
                os.path.join(
                    save_images_folder_path,
                    model,
                    f"{index}.png",
                ),
                model,
            )
        # """
        print("*" * 50)
    # '''
