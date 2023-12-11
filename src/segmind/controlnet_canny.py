import requests
from pathlib import Path

from utils.image_to_b64 import toB64
from segmind.settings import CONTROLNET_CANNY_URL as URL
from segmind.utils import choose_api_key
from segmind.settings import STABLE_DIFFUSION_NEGAVTIVE_PROMPT as NEGAVTIVE_PROMPT


def controlnet_canny(
    prompt: str,
    image_path: str,
    save_image_path: str,
    negative_prompt: str = NEGAVTIVE_PROMPT,
):
    """
    This cutting-edge model transcends traditional boundaries by employing
    the sophisticated canny edge detection method. Canny edge detection
    operates by pinpointing edges in an image through the identification
    of sudden shifts in intensity. Renowned for its prowess in accurately
    detecting edges while minimizing noise and erroneous edges, the method
    becomes even more potent when the preprocessor enhances its discernment
    by lowering the thresholds. Granting users an extraordinary level of
    control over image transformation parameters, the ControlNet Canny model
    is revolutionizing image editing and computer vision tasks, providing
    a customizable experience that caters to both subtle and dramatic
    image enhancements.

    At the core of the ControlNet Canny model lies the renowned canny
    edge detection mechanism. This image-to-image transformation model
    is meticulously crafted to detect and emphasize edges in images. Its
    design allows users to tweak and adjust parameters, ensuring that the
    edge detection is tailored to specific needs, be it subtle enhancements
    or bold transformations.

    Advantages:
    1. Precision Edge Detection: Utilizes the canny edge detection technique, known for its accuracy in identifying image edges.
    2. User Control: Offers users the ability to fine-tune parameters, ensuring customized edge enhancements.
    3. Versatility: Suitable for a myriad of applications, from artistic effects to technical image processing tasks.
    4. Real-time Manipulation: Allows for instantaneous adjustments, providing users with real-time feedback and results.

    Price: $ 0.002700 per request
    """
    # Check if the directory of save_image_path exists
    if not Path(save_image_path).parent.exists():
        raise FileNotFoundError(
            f"The directory {Path(save_image_path).parent} does not exist."
        )

    # Request payload
    data = {
        "image": toB64(image_path),
        "samples": "1",
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "scheduler": "UniPC",
        "num_inference_steps": "25",
        "guidance_scale": "7.5",
        "strength": "1",
        "seed": "3131738736286",
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
