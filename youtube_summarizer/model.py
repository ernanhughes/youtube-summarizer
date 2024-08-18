from pydantic import BaseModel, Field
from typing import Optional


class Transcript(BaseModel):
    id: Optional[int] = Field(None, description="Primary key, auto-incremented")
    video_id: str = Field(..., description="ID of the video")
    url: str = Field(..., description="URL of the transcript")
    language_code: str = Field('en', description="Language code, default is 'en'")
    is_generated: int = Field(1, description="Indicates if the transcript is auto-generated, default is 1")


class TranscriptText(BaseModel):
    id: Optional[int] = Field(None, description="Primary key, auto-incremented")
    video_id: str = Field(..., description="ID of the video")
    text_data: Optional[str] = Field(None, description="Transcript text data")
    start: Optional[float] = Field(None, description="Start time of the transcript segment")
    duration: Optional[float] = Field(None, description="Duration of the transcript segment")


class TranscriptFile(BaseModel):
    id: Optional[int] = Field(None, description="Primary key, auto-incremented")
    video_id: str = Field(..., description="ID of the video")
    data: Optional[bytes] = Field(None, description="Binary data of the transcript file")
