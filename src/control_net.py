from diffusers import StableDiffusionControlNetPipeline
from diffusers.utils import load_image
from PIL import Image
import cv2
import numpy as np
import os

# commandline_args = os.environ.get(
#     "COMMANDLINE_ARGS", "--skip-torch-cuda-test --no-half"
# )

image = load_image(
    "https://hf.co/datasets/huggingface/documentation-images/resolve/main/diffusers/input_image_vermeer.png"
)

image = np.array(image)

low_threshold = 100
high_threshold = 200

image = cv2.Canny(image, low_threshold, high_threshold)
image = image[:, :, None]
image = np.concatenate([image, image, image], axis=2)
canny_image = Image.fromarray(image)

from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    UniPCMultistepScheduler,
)
import torch

# Load or download the controlnet model
controlnet_path = "controlnet_model.pt"
if os.path.exists(controlnet_path):
    controlnet = ControlNetModel.from_pretrained(
        controlnet_path, torch_dtype=torch.float32, use_safetensors=True
    )
else:
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny",
        torch_dtype=torch.float32,
        use_safetensors=True,
    )
    controlnet.save_pretrained(controlnet_path)

print("ControlNet model loaded.")

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float32,
    use_safetensors=True,
).to("cpu")

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
# pipe.enable_model_cpu_offload()

print("Pipeline initialized.")

output = pipe("eyes closed", image=canny_image).images[0]

print("outpt type : ", type(output))

output.save("output.png")

print("Output saved to disk.")
