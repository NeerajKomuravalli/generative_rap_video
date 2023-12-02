# """
from llm.gpt import get_gpt_3_5_resp
from segmind.controlnet_canny import controlnet_canny
from segmind.stable_diffusion import stable_diffusion
from segmind.paragon import paragon
from segmind.settings import STABLE_DIFFUSION_STYLES as style
from segmind.prompts import STYLE_PICK
from stable_diffussion.stable_diffussion import text_to_image

if __name__ == "__main__":
    prompt = "A disco party with people having fun dancing."
    save_image_path = "./paragon.jpg"
    image_path = "/Users/neeraj/Downloads/test-image.jpg"
    # controlnet_canny(
    #     prompt,
    #     image_path,
    #     save_image_path,
    # )
    text_to_image()
# """
