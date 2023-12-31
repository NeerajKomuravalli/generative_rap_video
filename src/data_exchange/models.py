from pydantic import BaseModel


class ProjectStatus(BaseModel):
    project: bool = False
    original: str = ""
    audio_chunks: int = 0
    transcriptions: int = 0
    prompt: int = 0
    images: int = 0
    video: str = ""
