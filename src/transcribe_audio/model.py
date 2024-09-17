from typing import List
from pydantic import BaseModel


class Segment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class TranscriptAudioResponse(BaseModel):
    text: str
    segments: List[Segment]
    language: str
