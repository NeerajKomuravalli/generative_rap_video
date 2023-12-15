import modal
import librosa


class TranscribeAudio:
    def __init__(self):
        self.transcribe_to_eng = modal.Function.lookup(
            "transcribe-whisper",
            "Model.transcribe_in_english",
        )
        self.transcribe_to_or = modal.Function.lookup(
            "transcribe-whisper",
            "Model.transcribe",
        )

    def _read_audio(self, audio_path: str):
        audio, sr = librosa.load(
            audio_path,
            sr=None,
        )
        return audio

    def transcribe_audio_to_eng(self, audio_path: str):
        result = self.transcribe_to_eng.remote(self._read_audio(audio_path))
        return result

    def transcribe_audio(self, audio_path: str):
        result = self.transcribe_to_or.remote(self._read_audio(audio_path))
        return result
