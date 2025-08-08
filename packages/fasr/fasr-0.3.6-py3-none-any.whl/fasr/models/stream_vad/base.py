from fasr.models.base import StreamModel
from fasr.data import AudioChunk
from abc import abstractmethod
from typing import Iterable


class StreamVADModel(StreamModel):
    chunk_size_ms: int = 100
    sample_rate: int = 16000
    max_end_silence_time: int = 500
    db_threshold: int | None = None

    @abstractmethod
    def detect_chunk(chunk: AudioChunk) -> Iterable[AudioChunk]:
        raise NotImplementedError

    @property
    def chunk_size(self) -> int:
        return self.chunk_size_ms * self.sample_rate // 1000
