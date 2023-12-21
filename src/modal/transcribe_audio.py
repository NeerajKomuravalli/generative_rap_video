import numpy as np

from modal import Image, Stub, method

image = (
    Image.debian_slim()
    .apt_install("git")
    .pip_install(
        "git+https://github.com/openai/whisper.git",
        "dacite",
        "jiwer",
        "ffmpeg-python",
        "gql[all]~=3.0.0a5",
        "pandas",
        "loguru==0.6.0",
        "torchaudio==2.1.0",
    )
    .apt_install("ffmpeg")
    .pip_install("ffmpeg-python")
)

stub = Stub("transcribe-whisper", image=image)

MODELS = [
    "tiny.en",
    "tiny",
    "base.en",
    "base",
    "small.en",
    "small",
    "medium.en",
    "medium",
    "large-v1",
    "large-v2",
    "large-v3",
    "large",
]


@stub.cls(gpu="any", container_idle_timeout=240)
class Model:
    def __enter__(self, model_name: str = "large-v3"):
        import torch
        import whisper

        if model_name not in MODELS:
            raise Exception("Invalid model name")

        self.use_gpu = torch.cuda.is_available()
        device = "cuda" if self.use_gpu else "cpu"
        self.model = whisper.load_model(
            model_name,
            device=device,
        )

    @method()
    def transcribe_in_english(self, audio_ndarry: np.ndarray):
        """
        Transcribe an audio file using a speech-to-text model to english languge.
        """
        result = self.model.transcribe(
            audio_ndarry,
            fp16=self.use_gpu,
            task="translate",
        )
        return result

    @method()
    def transcribe(self, audio_ndarry: np.ndarray):
        """
        Transcribe an audio file using a speech-to-text model.
        """
        result = self.model.transcribe(
            audio_ndarry,
            fp16=self.use_gpu,
        )
        return result


@stub.local_entrypoint()
def main(audio_path: str):
    import librosa

    audio, sr = librosa.load(audio_path, sr=None)
    print(Model().transcribe.remote(audio))
