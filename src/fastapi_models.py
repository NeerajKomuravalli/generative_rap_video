from enum import Enum

from pydantic import BaseModel
from transcribe_audio.model import TranscriptAudioResponse


class TranslationLanguage(str, Enum):
    english = "en"
    hindi = "hi"
    original = ""


class TranscriptionRequest(BaseModel):
    audio_path: str
    language: TranslationLanguage = TranslationLanguage.english


class TranscriptionAPIResponse(BaseModel):
    audio_path: str
    transcription: TranscriptAudioResponse
