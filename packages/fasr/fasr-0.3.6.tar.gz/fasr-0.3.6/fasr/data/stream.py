import ctypes
from typing import List
from uuid import uuid4

from loguru import logger
import numpy as np

from .audio import AudioChunk, AudioChunkList
from .waveform import Waveform


class AudioBytesStream:
    """
    Buffer and chunk audio byte data into fixed-size audiochunk(frame).

    This class is designed to handle incoming audio data in bytes,
    buffering it and producing audio frames of a consistent size.
    It is mainly used to easily chunk big or too small audio frames
    into a fixed size, helping to avoid processing very small frames
    (which can be inefficient) and very large frames (which can cause
    latency or processing delays). By normalizing frame sizes, it
    facilitates consistent and efficient audio data processing.
    """

    def __init__(
        self,
        sample_rate: int,
        num_channels: int = 1,
        chunk_size_ms: int = 100,
    ) -> None:
        """
        Initialize an AudioByteStream instance.

        Parameters:
            sample_rate (int): The audio sample rate in Hz.
            num_channels (int): The number of audio channels.
            samples_per_channel (int, optional): The number of samples per channel in each frame.
                If None, defaults to `sample_rate // 10` (i.e., 100ms of audio data).

        The constructor sets up the internal buffer and calculates the size of each frame in bytes.
        The frame size is determined by the number of channels, samples per channel, and the size
        of each sample (assumed to be 16 bits or 2 bytes).
        """
        self._sample_rate = sample_rate
        self._num_channels = num_channels
        samples_per_channel = sample_rate // 1000 * chunk_size_ms

        self._bytes_per_frame = (
            num_channels * samples_per_channel * ctypes.sizeof(ctypes.c_int16)
        )
        self._buf = bytearray()
        self._id = uuid4().hex

    def push(self, data: bytes) -> List[AudioChunk]:
        """
        Add audio data to the buffer and retrieve fixed-size frames.

        Parameters:
            data (bytes): The incoming audio data to buffer.

        Returns:
            AudioChunkList: A list of `AudioFrame` objects, each containing
            a fixed-size chunk of audio data.
        """
        self._buf.extend(data)

        chunks = AudioChunkList()
        while len(self._buf) >= self._bytes_per_frame:
            frame_data = self._buf[: self._bytes_per_frame]
            self._buf = self._buf[self._bytes_per_frame :]
            frame_data = np.frombuffer(
                frame_data,
                dtype=np.int16,
            ).astype(np.float32)
            chunks.append(
                AudioChunk(
                    stream_id=self._id,
                    waveform=Waveform(data=frame_data, sample_rate=self._sample_rate),
                )
            )

        return chunks

    def flush(self) -> AudioChunkList:
        """
        Flush the buffer and retrieve any remaining audio data as a final audio chunk.
        """
        chunks = AudioChunkList()
        if len(self._buf) == 0:
            return chunks

        if len(self._buf) % (2 * self._num_channels) != 0:
            logger.warning("AudioByteStream: incomplete frame during flush, dropping")
            return chunks

        chunks.append(
            AudioChunk(
                stream_id=self._id,
                waveform=Waveform(data=self._buf, sample_rate=self._sample_rate),
                is_last=True,
            )
        )
        self._buf.clear()
        return chunks


AudioBytesBuffer = (
    AudioBytesStream  # AudioBytesStream is deprecated, use AudioBytesBuffer instead.
)
