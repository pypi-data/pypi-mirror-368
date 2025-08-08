from pydantic import BaseModel
from typing import Literal


class AudioChunkResponse(BaseModel):
    text: str
    state: (
        Literal[
            "segment_start", "segment_end", "interim_transcript", "final_transcript"
        ]
        | None
    ) = None
    lang: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    confidence: float | None = None


class TranscriptionResponse(BaseModel):
    code: Literal[0, -1] = 0
    msg: str = "success"
    data: AudioChunkResponse | None = None
