from pydantic import BaseModel


class ProjectStatus(BaseModel):
    project: bool = False
    original: str = ""
    audio_chunks: int = 0
    transcriptions: int = 0
    prompt: int = 0
    images: int = 0
    video: str = ""


class ProjectData(BaseModel):
    name: str = ""
    bpm: int = 0
    chunk_count: int = 0
    last_updated: str = ""
