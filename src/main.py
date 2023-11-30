from llm.gpt import get_gpt_3_5_resp
from segmind.paragon import paragon
from segmind.settings import STABLE_DIFFUSION_STYLES as style
from segmind.prompts import STYLE_PICK

if __name__ == "__main__":
    prompt = "A photo of 30 year old man, thin and fit with a lean body looking dead into the camera with vengence"
    save_image_path = "./paragon.jpg"

    paragon(
        prompt,
        save_image_path,
    )
