import os
import json
from pathlib import Path

from llm.gpt import GPT3Chat
from video_gen.utils import split_srt_chunk
from prompt_generator.metrics_mule_prompt_for_images import prompt_with_summary
from prompt_generator.intro_outro_prompt_gen import prompt as intro_outro_prompt


def srt_to_stable_diffusion_prompt(srt_file_path: str, save_prompt_json_path: str):
    """
    Converts the contents of an SRT (SubRip Text) file into prompts for a Stable Diffusion model.

    This function processes an SRT file, typically containing subtitles or lyrics, and uses a series of GPT-3.5-based agents to generate prompts suitable for a Stable Diffusion model. It handles special cases like music-only sections and categorizes content into intro, outro, and regular content. The generated prompts are saved as a JSON file.

    Parameters:
    srt_file_path (str): Path to the SRT file containing subtitles or lyrics.
    save_prompt_json_path (str): Path where the generated JSON file with prompts will be saved.

    The function performs several steps:
    1. Validates the provided paths.
    2. Reads and splits the SRT file into chunks.
    3. Summarizes the lyrics using a GPT-3.5 agent.
    4. Generates prompts for each chunk using different instances of GPT-3.5 agents, tailored for intro, outro, and regular content.
    5. Saves the generated prompts as a JSON file.

    The resulting JSON file contains a dictionary where each key corresponds to a chunk index from the SRT file, and the value is the generated prompt for that chunk.

    Exceptions:
    - Raises an Exception if the paths provided for the SRT file or the JSON save path are invalid.

    Note:
    - This function requires the GPT-3.5 language model and its variants (e.g., gpt-3.5-turbo, gpt-3.5-turbo-16k) for generating summaries and prompts.
    - The logic to determine whether a chunk is part of the intro or outro is currently simple and may not be scalable for all SRT files.

    Dependencies:
    - os, json, Path (from pathlib) for file and path handling.
    - GPT3Chat (a hypothetical class or module) for interacting with GPT-3.5 agents.
    """

    # Check if save_prompt_json_path is valid
    if not Path(save_prompt_json_path).parent.exists():
        raise Exception(f"{save_prompt_json_path} is not a valid path")

    # Check for srt file precense
    if not os.path.exists(srt_file_path):
        raise Exception("srt file doesn't exist")

    # Read srt file with lyrics
    with open(srt_file_path, "r") as file:
        srt_text = file.read()

    # Split the file into chunks
    chunks = srt_text.strip().split("\n\n")

    content = ""
    for _, chunk in enumerate(chunks):
        _, _, subtitle_text = split_srt_chunk(chunk)

        if subtitle_text.strip() == "Music":
            continue

        content += "\n" + subtitle_text

    prompt = f"""
    You are an expert in summarizing the lyrics of rap music. Below is the english translation of the hindi rap track.
    Below are the lyrics:
    {content}
    Summarize the track
    """

    # Get summaray of the track
    print("Generating summary")
    summary_gpt_agent = GPT3Chat("gpt-3.5-turbo")
    summary = summary_gpt_agent.get_response(prompt)
    prompt = prompt_with_summary % (summary)

    # Use sa saperate instance of gpt
    print("Initiating GPT for for lyrics")
    stable_diff_prompt_gen_agent = GPT3Chat("gpt-3.5-turbo-16k")
    response = stable_diff_prompt_gen_agent.get_response(prompt)

    # Use a saperate instance of gpt for intro
    print("Initiating GPT for for intro")
    intro_prompt = intro_outro_prompt % (summary, "intro")
    intro_stable_diff_prompt_gen = GPT3Chat("gpt-3.5-turbo-16k")
    intro_stable_diff_prompt_gen.get_response(intro_prompt)

    # Use a saperate instance of gpt for outro
    print("Initiating GPT for for outro")
    outro_prompt = intro_outro_prompt % (summary, "outro")
    outro_stable_diff_prompt_gen = GPT3Chat("gpt-3.5-turbo-16k")
    outro_stable_diff_prompt_gen.get_response(outro_prompt)

    responses = {}
    for _, chunk in enumerate(chunks):
        index, _, subtitle_text = split_srt_chunk(chunk)
        print(f"Processing : {index}")
        # NOTE: TODO: The logic to decide if it's intro or outro is not relly scalable and should be changed
        if subtitle_text.strip() == "Music":
            if int(index) < len(chunks) / 2:
                response = intro_stable_diff_prompt_gen.get_response("Next")
            else:
                response = outro_stable_diff_prompt_gen.get_response("Next")
        else:
            response = stable_diff_prompt_gen_agent.get_response(subtitle_text)
        responses[index] = response

    json.dump(responses, open(save_prompt_json_path, "w"))

    return responses
