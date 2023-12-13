import os
import json

from pathlib import Path
from segmind.stable_diffusion import stable_diffusion


def stable_diffusion_to_frames(
    save_prompt_json_path: str,
    save_images_folder_path: str,
    model: str,
):
    # Check if save_prompt_json_path is valid
    if not os.path.exists(save_prompt_json_path):
        raise Exception(f"{save_prompt_json_path} is not a valid path")

    # Check if save_images_folder_path is valid
    if not os.path.exists(save_images_folder_path):
        raise Exception(f"{save_images_folder_path} is not a valid path")

    stable_diff_prompt = json.load(open(save_prompt_json_path))
    for index in stable_diff_prompt:
        prompt = stable_diff_prompt[index]
        # Pre process the prompt
        prompt = (
            prompt.replace("Photorealistic Images prompt:", "")
            .replace("Prompt:", "")
            .replace("Photorealistic Images:\nOutro Scene:", "")
            .replace("Done", "")
            .replace("Next", "")
            .strip()
        )
        print(f"Generating {index}")
        stable_diffusion(
            prompt,
            os.path.join(
                save_images_folder_path,
                f"{index}.png",
            ),
            model,
        )
