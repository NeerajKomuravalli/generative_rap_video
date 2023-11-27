from pathlib import Path
from diffusers.utils import load_image
from PIL import Image as Im
import cv2
import numpy as np
from modal import (
    stub,
    Image,
    Stub,
    method,
)
from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    UniPCMultistepScheduler,
)
import torch


def download_models():
    from huggingface_hub import snapshot_download

    ignore = ["*.bin", "*.onnx_data", "*/diffusion_pytorch_model.safetensors"]
    # For canny
    snapshot_download("lllyasviel/sd-controlnet-canny", ignore_patterns=ignore)

    snapshot_download("runwayml/stable-diffusion-v1-5", ignore_patterns=ignore)


image = (
    Image.debian_slim(python_version="3.10")
    .pip_install(
        "gradio==3.16.2",
        "albumentations==1.3.0",
        "opencv-contrib-python",
        "imageio==2.9.0",
        "imageio-ffmpeg==0.4.2",
        "pytorch-lightning==1.5.0",
        "omegaconf==2.1.1",
        "test-tube>=0.7.5",
        "streamlit==1.12.1",
        "einops==0.3.0",
        "diffusers",
        "transformers",
        "webdataset==0.2.5",
        "kornia==0.6",
        "open_clip_torch==2.0.2",
        "invisible-watermark>=0.1.5",
        "streamlit-drawable-canvas==0.8.0",
        "torchmetrics==0.6.0",
        "timm==0.6.12",
        "addict==2.4.0",
        "yapf==0.32.0",
        "prettytable==3.6.0",
        "safetensors",
        "basicsr==1.4.2",
        "tqdm~=4.64.1",
    )
    # xformers library offers performance improvement.
    .pip_install("xformers", pre=True)
    .apt_install("git")
    .pip_install("git+https://github.com/huggingface/accelerate.git")
    # Here we place the latest ControlNet repository code into /root.
    # Because /root is almost empty, but not entirely empty, `git clone` won't work,
    # so this `init` then `checkout` workaround is used.
    .run_commands(
        "cd /root && git init .",
        "cd /root && git remote add --fetch origin https://github.com/lllyasviel/ControlNet.git",
        "cd /root && git checkout main",
    )
    .apt_install("ffmpeg", "libsm6", "libxext6")
    .run_function(download_models)
)
stub = Stub(name="controlnet-canny", image=image)


@stub.cls(gpu="t4", container_idle_timeout=240, timeout=600)
class Model:
    def __enter__(self):
        self.controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16
        )
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=self.controlnet,
            torch_dtype=torch.float16,
        ).to("cuda")

    @method()
    def inference(self, prompt: str, content_image):
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        self.pipe.enable_model_cpu_offload()
        output = self.pipe(prompt, image=content_image).images[0]
        return output


def apply_canny(image_path: str):
    image = load_image(image_path)

    image = np.array(image)

    low_threshold = 100
    high_threshold = 200

    image = cv2.Canny(image, low_threshold, high_threshold)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    return Im.fromarray(image)


@stub.local_entrypoint()
def main(prompt: str, control_image_path: str, save_image_path: str):
    control_image = apply_canny(control_image_path)
    image_bytes = Model().inference.remote(prompt, control_image)

    # check if the fodler of the save_image_path exists
    output_path = Path(save_image_path)
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    print(f"Saving it to {output_path}")
    with open(output_path, "wb") as f:
        f.write(image_bytes)
