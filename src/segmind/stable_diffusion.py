import os
import requests
from pathlib import Path

from dotenv import load_dotenv

from segmind.settings import STABLE_DIFFUSION_NEGAVTIVE_PROMPT as NEGAVTIVE_PROMPT
from segmind.settings import STABLE_DIFFUSION_URL as URL
from segmind.settings import STABLE_DIFFUSION_STYLES as STYLES
from segmind.prompts import STYLE_PICK
from segmind.utils import choose_api_key
from llm.gpt import get_gpt_3_5_resp


load_dotenv()


def stable_diffusion(
    prompt: str,
    save_image_path: str,
    style: str = STYLES[0],
    negative_prompt: str = NEGAVTIVE_PROMPT,
    automatic_style_select: bool = False,
):
    """
    Stable Diffusion SDXL 1.0, a product of Stability AI, is a groundbreaking
    development in the realm of image generation. It's a quantum leap
    from its predecessor, Stable Diffusion 1.5 and 2.1, boasting superior
    advancements in image and facial composition. This revolutionary tool
    leverages a latent diffusion model for text-to-image synthesis,
    rendering it an essential asset in the visual arts landscape in 2023.
    The real magic lies in its ability to create descriptive images from
    succinct prompts and generate words within images, setting a new
    standard for AI-generated visuals.

    Stable Diffusion SDXL 1.0 use cases
    1. Art and Design: Create stunning visuals and graphics for digital media.
    2. Marketing and Advertising: Generate attention-grabbing imagery for campaigns.
    3. Entertainment and Gaming: Develop detailed graphics for video games and interactive content.
    4. Education: Simplify complex concepts with easy-to-understand visuals.
    5. Research: Visualize data and research findings for better comprehension.

    Price: $ 0.010000 per request
    """
    # Check if the directory of save_image_path exists
    if not Path(save_image_path).parent.exists():
        raise FileNotFoundError(
            f"The directory {Path(save_image_path).parent} does not exist."
        )

    # Choose the style using LLM (GPT-3.5)
    if automatic_style_select:
        style_selected = get_gpt_3_5_resp(
            message=STYLE_PICK.format(prompt=prompt, style=STYLES)
        )
        if style_selected in STYLES:
            style = style_selected

    # Request payload
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "style": style,
        "samples": 1,
        "scheduler": "UniPC",
        "num_inference_steps": 25,
        "guidance_scale": "8",
        "strength": 0.2,
        "high_noise_fraction": 0.8,
        # "seed": "468685",
        "img_width": "1024",
        "img_height": "1024",
        "refiner": True,
        "base64": False,
    }

    response = requests.post(
        URL,
        json=data,
        headers={
            "x-api-key": choose_api_key(),
        },
    )

    if response.status_code == 200:
        with open(save_image_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"Request failed with status code {response.status_code}")
