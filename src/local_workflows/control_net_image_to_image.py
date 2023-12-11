import os
import torch
import numpy as np

from transformers import pipeline
from diffusers.utils import load_image

from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline,
    ControlNetModel,
    UniPCMultistepScheduler,
)
import torch

commandline_args = os.environ.get(
    "COMMANDLINE_ARGS", "--skip-torch-cuda-test --no-half"
)

image = load_image(
    "https://pub-3626123a908346a7a8be8d9295f44e26.r2.dev/generations/ab9d3497-ab9b-42da-8e71-d96774d51de6-0.png"
).resize((768, 768))


def get_depth_map(image, depth_estimator):
    image = depth_estimator(image)["depth"]
    image = np.array(image)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    detected_map = torch.from_numpy(image).float() / 255.0
    depth_map = detected_map.permute(2, 0, 1)
    return depth_map


depth_estimator = pipeline("depth-estimation")
depth_map = get_depth_map(image, depth_estimator).unsqueeze(0).half().to("cpu")

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11f1p_sd15_depth",
    torch_dtype=torch.float64,
    use_safetensors=True,
)
pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float64,
    use_safetensors=True,
).to("cpu")

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
# pipe.enable_model_cpu_offload()

output = pipe(
    "people smoking while dancing in the club",
    image=image,
    control_image=depth_map,
).images[0]

output.save("output_control_net_image_to_image_w_depth.png")
