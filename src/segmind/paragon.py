import os
import requests
from pathlib import Path

from dotenv import load_dotenv


from segmind.settings import STABLE_DIFFUSION_NEGAVTIVE_PROMPT as NEGAVTIVE_PROMPT
from segmind.settings import PARAGON_URL as URL
from segmind.utils import choose_api_key

load_dotenv()


def paragon(
    prompt: str,
    save_image_path: str,
    negative_prompt: str = NEGAVTIVE_PROMPT,
):
    """
    About the model:
    The Paragon v1.0 model is a boon for artists seeking photorealism in
    their work. This model is built on the Stable Diffusion 1.5 framework.
    It is renowned for its ability to generate super realistic portraits
    that are really close to real photographs. The model's strong
    contrast is a feature that has garnered much appreciation. It is
    versatile, capable of generating portraits in various styles, ages,
    and clothing. The LoRa versions of this model have been particularly
    well-received for their performance.

    Use cases:
    1. Digital Art Creation: Artists can use this model to create realistic portraits, adding a touch of realism to their digital art.
    2. Character Generation for Video Games or Animations: Game developers and animators can use this model to generate diverse characters, enhancing the visual appeal of their games or animations.
    3. Social Media or Virtual Reality Avatars: The model can be used to produce unique avatars for users on social media or virtual reality platforms.
    4. Character Design for Books or Graphic Novels: Authors and graphic novelists can use this model to design fictional characters, bringing their stories to life.
    5. Fashion Design Visualization: Fashion designers can use this model to visualize different styles and outfits on various models, aiding in the design process.

    How to create consistent results:
    When you mention the age of the person, enthinicty, demographics, and name with the same seed value it gives consisten results.

    Price: $ 0.003000 per request
    """
    # Check if the directory of save_image_path exists
    if not Path(save_image_path).parent.exists():
        raise FileNotFoundError(
            f"The directory {Path(save_image_path).parent} does not exist."
        )

    # Request payload
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "scheduler": "dpmpp_sde_ancestral",
        "num_inference_steps": "25",
        "guidance_scale": "7.5",
        "samples": "1",
        "seed": "945216760",
        "img_width": "512",
        "img_height": "768",
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
