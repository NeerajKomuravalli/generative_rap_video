from pathlib import Path

from modal import Image, Stub, method
from torch.utils.data import Dataset
import numpy as np

MODEL_ID = "openai/whisper-large-v3"


def download_models():
    from huggingface_hub import snapshot_download

    ignore = ["*.bin", "*.onnx_data", "*/diffusion_pytorch_model.safetensors"]
    snapshot_download(
        MODEL_ID,
        ignore_patterns=ignore,
    )


image = (
    Image.debian_slim()
    .apt_install(
        "libglib2.0-0", "libsm6", "libxrender1", "libxext6", "ffmpeg", "libgl1"
    )
    .pip_install(
        "torch",
        "transformers",
        "safetensors",
        "accelerate",
    )
    .run_function(download_models)
)

stub = Stub("transcribe-whisper-hf", image=image)


@stub.cls(gpu="any", container_idle_timeout=240)
class Model:
    def __enter__(self):
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        from torch.utils.data import Dataset

        self.device = "cuda:0"

        # Load base model
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(MODEL_ID)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch.float16,
            device=self.device,
        )

    @method()
    def transcribe_in_english(self, audio_ndarry: np.ndarray):
        result = self.pipe(
            audio_ndarry,
            generate_kwargs={"task": "translate"},
            return_timestamps=True,
        )

        return result

    @method()
    def transcribe(self, audio_ndarry: np.ndarray):
        result = self.pipe(
            audio_ndarry,
            return_timestamps=True,
        )

        return result


@stub.local_entrypoint()
def main(audio_path: str):
    import json
    import librosa

    audio, sr = librosa.load(audio_path, sr=None)
    result = Model().inference.remote(audio)

    json.dump(result, Path("translated.json").open("w"))
