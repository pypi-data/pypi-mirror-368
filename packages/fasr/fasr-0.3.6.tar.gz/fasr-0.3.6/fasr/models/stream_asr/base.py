from typing import Iterable
from fasr.models.base import StreamModel
from fasr.data import AudioChunk, AudioToken
from abc import abstractmethod


class StreamASRModel(StreamModel):
    """流式语音识别模型基类"""

    chunk_size_ms: int = None

    @abstractmethod
    def transcribe_chunk(self, chunk: AudioChunk) -> Iterable[AudioToken]:
        raise NotImplementedError
