import os
import json
from pathlib import Path

from llm.gpt import GPT3Chat
from video_gen.utils import split_srt_chunk
from prompt_generator.metrics_mule_prompt_for_images import prompt_with_summary
from prompt_generator.intro_outro_prompt_gen import prompt as intro_outro_prompt


def chunks_to_stable_diffusion_prompt(transcript_list: [str]):
    """
    Generate stable diffusion prompts from a list of transcript chunks.

    This function accepts a list of transcript chunks, generates a summary of the entire track,
    and then uses that summary to generate stable diffusion prompts for each chunk.

    It uses separate instances of the GPT-3.5-turbo model to generate the summary, the lyrics prompts,
    the intro prompts, and the outro prompts.

    Args:
        transcript_list (list[str]): A list of transcript chunks.

    Returns:
        dict: A dictionary where the keys are the chunk indices and the values are the generated prompts.
    """
    # Get summaray of the track
    print("Generating summary")
    summary_gpt_agent = GPT3Chat("gpt-3.5-turbo")
    # Create prompt for summary
    # Removing only music part as that would not contribute to the summary
    total_transcript = ""
    for chunk in transcript_list:
        if chunk.strip() in ["Music", ""]:
            continue
        total_transcript += "\n" + chunk

    total_transcript = "\n".join(transcript_list)
    summary_prompt = f"""
    You are an expert in summarizing the lyrics of rap music. Below is the english translation of the hindi rap track.
    Below are the lyrics:
    {total_transcript}
    Summarize the track
    """
    summary = summary_gpt_agent.get_response(summary_prompt)

    # Use sa saperate instance of gpt
    print("Initiating GPT for for lyrics")
    stable_diff_prompt_gen_agent = GPT3Chat("gpt-3.5-turbo-16k")
    prompt = prompt_with_summary % (summary)
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
    for index, subtitle_text in enumerate(transcript_list):
        print(f"Processing : {index}")
        # NOTE: TODO: The logic to decide if it's intro or outro is not relly scalable and should be changed
        if subtitle_text.strip() in ["Music", ""]:
            if int(index) < len(transcript_list) / 2:
                response = intro_stable_diff_prompt_gen.get_response("Next")
            else:
                response = outro_stable_diff_prompt_gen.get_response("Next")
        else:
            response = stable_diff_prompt_gen_agent.get_response(subtitle_text)
        # We are saving the chunks with index starting from 1 so we add one in dict as well
        responses[index + 1] = response

    return responses


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

    transcript_chunks = []
    for _, chunk in enumerate(chunks):
        _, _, subtitle_text = split_srt_chunk(chunk)
        transcript_chunks.append(chunk)

    responses = chunks_to_stable_diffusion_prompt(transcript_chunks)

    json.dump(responses, open(save_prompt_json_path, "w"))

    return responses
