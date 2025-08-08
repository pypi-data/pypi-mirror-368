from __future__ import annotations
from typing import (
    Optional,
    List,
    Iterable,
    Union,
    Dict,
    Literal,
    Generator,
    Any,
    FrozenSet,
)
import re
import requests
from io import BytesIO
import os
from functools import lru_cache
from pathlib import Path

from typing_extensions import Self
import librosa
from pydub import AudioSegment
from joblib import Parallel, delayed
from pydantic import ConfigDict, Field, model_validator
from loguru import logger
from torch import Tensor
from torchaudio.functional import resample as torchaudio_resample
from docarray import BaseDoc, DocList
from docarray.typing import NdArray, ID
from docarray.utils.filter import filter_docs
import numpy as np

from .waveform import Waveform


class AudioToken(BaseDoc):
    """Audio token object that represents the smallest unit of an audio file, which must have the text that the speech recognizer recognized.

    Args:
        start_ms (int): Start ms of the token.
        end_ms (int): End ms of the token.
        text (str): Text of the token.
        waveform (NdArray): Waveform of the token.
        follow (str): Follow char. Defaults to " ".
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: ID | None = None
    text: str = Field(..., description="Text of the token.")
    start_ms: int | None = Field(None, description="Start time of the token.")
    end_ms: int | None = Field(None, description="End time of the token.")
    waveform: Waveform | None = Field(
        None, description="Waveform of the token.", exclude=True
    )
    follow: Optional[str] = Field(" ", description="Follow char.")

    @property
    def duration_ms(self):
        """Get the duration of the token in milliseconds."""
        return self.end_ms - self.start_ms

    def is_punctuation(self) -> bool:
        return re.match(r"[^\w\s]", self.text) is not None


class AudioTokenList(DocList):
    @property
    def duration_ms(self):
        """Get the total duration of all the tokens in milliseconds."""
        return sum([token.duration_ms for token in self])

    @property
    def duration(self):
        """Get the total duration of all the tokens in seconds."""
        return self.duration_ms / 1000

    @property
    def text(self):
        """Get the text of all the tokens."""
        text = ""
        for t in self:
            text += t.text
            text += t.follow
        return text.strip()  # remove the last space


class AudioSpan(BaseDoc):
    """Audio span object that represents a segment of an audio file, which must have the start and end time.

    Args:
        start_ms (int): Start ms of the segment.
        end_ms (int): End ms of the segment.
        waveform (NdArray): Waveform of the segment.
        feats (NdArray): Features of the segment.
        tokens (AudioTokenList): Tokens of the segment.
        sample_rate (int): Sample rate of the segment.
        is_last (bool): Whether the segment is the last segment. Defaults to False.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    id: ID | None = None
    start_ms: float | int | None = Field(None, description="Start time of the segment.")
    end_ms: float | int | None = Field(None, description="End time of the segment.")
    waveform: Waveform | None = Field(
        None, description="Waveform of the segment.", exclude=True
    )

    feats: NdArray | Tensor | None = Field(None, description="Features of the segment.")
    scores: NdArray | Tensor | None = Field(None, description="Scores of the segment.")
    tokens: AudioTokenList[AudioToken] | None = Field(
        None, description="Tokens of the segment."
    )

    language: str | None = None
    emotion: str | None = None
    type: str | None = None
    is_last: bool | None = None
    is_bad: bool | None = None
    bad_reason: str | None = None
    bad_component: str | None = None

    def display(self):
        """Display the segment."""
        from IPython.display import Audio as IPAudio

        return IPAudio(data=self.waveform.data, rate=self.sample_rate)

    @property
    def sample_rate(self) -> int | None:
        """Get the sample rate of the segment."""
        if self.waveform is None:
            return None
        return self.waveform.sample_rate

    @property
    def duration_ms(self):
        """Get the duration of the segment in milliseconds."""
        return self.end_ms - self.start_ms

    @property
    def duration(self):
        """Get the duration of the segment in seconds."""
        return self.duration_ms / 1000

    @property
    def text(self):
        """Get the text of all the tokens."""
        if hasattr(self, "_text"):
            return self._text
        text = ""
        if self.tokens is None:
            return text
        for t in self.tokens:
            text += t.text
            text += t.follow
        return text.strip()  # remove the last space

    @text.setter
    def text(self, text: str):
        self._text = text

    def __lt__(self, other: "AudioSpan") -> bool:
        """Compare the duration of the segment with another segment. like `self < other`.

        Args:
            other (AudioSpan): Another segment.

        Returns:
            bool: Whether the duration of the segment is less than the duration of the other segment.
        """
        return self.duration_ms < other.duration_ms

    def __gt__(self, other: "AudioSpan") -> bool:
        """Compare the duration of the segment with another segment. like `self > other`.

        Args:
            other (AudioSpan): Another segment.

        Returns:
            bool: Whether the duration of the segment is greater than the duration of the other segment.
        """
        return self.duration_ms > other.duration_ms

    def __getitem__(self, index: int) -> Optional[AudioToken]:
        """Get the token at the index.

        Args:
            index (int): Index of the token.

        Returns:
            AudioToken: Token at the index.
        """
        if self.tokens is None:
            return None
        return self.tokens[index]

    def __len__(self) -> int:
        """Get the number of tokens in the segment.

        Returns:
            int: Number of tokens in the segment.
        """
        if self.tokens is None:
            return 0
        return len(self.tokens)


class AudioSpanList(DocList):
    @property
    def duration_ms(self):
        """Get the total duration of all the spans in milliseconds."""
        return sum([span.duration_ms for span in self])

    @property
    def duration(self):
        """Get the total duration of all the spans in seconds."""
        return self.duration_ms / 1000

    @property
    def padded_duration_ms(self):
        """Get the padded duration of all the spans in milliseconds."""
        all_durations = [span.duration_ms for span in self]
        if len(all_durations) == 0:
            return 0
        duration = max(all_durations) * len(all_durations)
        return duration

    @property
    def max_duration_ms(self):
        """Get the maximum duration of all the spans in milliseconds."""
        all_durations = [span.duration_ms for span in self]
        if len(all_durations) == 0:
            return 0
        return max(all_durations)

    @property
    def text(self):
        """Get the text of all the spans."""
        _text = ""
        for span in self:
            _text += span.text
        return _text


class AudioChannel(BaseDoc):
    """Audio channel object that represents a channel of an audio file."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    id: ID | None = None
    raw_text: str | None = Field(None, description="Text of the channel.")
    waveform: Waveform | None = Field(
        None, description="Waveform of the audio file.", exclude=True
    )
    segments: Optional[AudioSpanList[AudioSpan]] = Field(
        None, description="Segments of the audio file provided by the detector."
    )
    sents: Optional[AudioSpanList[AudioSpan]] = Field(
        None, description="Sentences of the audio file provided by the sentencizer."
    )
    tokens: AudioTokenList[AudioToken] | None = Field(
        default=None,
        description="Tokens of the audio file provided by the recognizer.",
    )
    stream: Iterable[AudioToken] | None = Field(
        None, description="Stream of tokens of the audio file."
    )
    is_last: Optional[bool] = Field(
        None, description="Whether the channel is the last."
    )
    is_bad: Optional[bool] = Field(None, description="Whether the channel is bad.")
    bad_reason: Optional[Union[str, Exception]] = Field(
        None, description="Reason why the audio file is bad."
    )

    @property
    def duration(self):
        """Get the duration of the audio file in seconds."""
        return self.waveform.duration

    @property
    def duration_s(self):
        """Get the duration of the audio file in seconds."""
        return self.duration

    @property
    def duration_ms(self):
        """Get the duration of the audio file in milliseconds."""
        return self.duration * 1000

    @property
    def start_ms(self):
        return 0

    @property
    def end_ms(self):
        return self.duration_ms

    @property
    def text(self):
        """Get the text of all the spans."""
        if self.raw_text is not None:
            return self.raw_text
        if self.sents:
            text = ""
            for sent in self.sents:
                text += sent.text
            return text
        elif self.segments:
            text = ""
            for seg in self.segments:
                text += seg.text
            return text
        elif self.tokens:
            text = ""
            for token in self.tokens:
                text += token.text + token.follow
            return text
        else:
            return ""

    @text.setter
    def text(self, text: str):
        self.raw_text = text

    def resample(self, sample_rate: int) -> "AudioChannel":
        """Resample the audio channel waveform to the target sample rate.

        Args:
            sample_rate (int): Target sample rate.
        """
        self.waveform = self.waveform.resample(sample_rate)
        return self

    def resample_torch(self, sample_rate: int) -> "AudioChannel":
        """Resample the audio channel waveform to the target sample rate.

        Args:
            sample_rate (int): Target sample rate.
        """
        self.waveform = torchaudio_resample(
            self.waveform,
            self.sample_rate,
            sample_rate,
            lowpass_filter_width=16,
            rolloff=0.85,
            resampling_method="sinc_interp_kaiser",
            beta=8.555504641634386,
        )
        self.sample_rate = sample_rate
        return self

    def align_bad(self) -> bool:
        """Check if the audio channel is bad."""
        for span in self.segments:  # recognizer报错
            if span.is_bad:
                self.is_bad = True
                self.bad_reason = span.bad_reason
                return True
        for span in self.sents:  # sentencizer报错
            if span.is_bad:
                return True
        for span in self.steps:  # detector报错
            if span.is_bad:
                return True
        return False

    def is_recognized(self) -> bool:
        """Check if the audio channel is recognized."""
        if not self.segments:
            return False
        for span in self.segments:
            span: AudioSpan
            if span.tokens is None:
                return False
        return True

    def display(self, start_ms: float | None = None, end_ms: float | None = None):
        """Display the audio channel."""
        from IPython.display import Audio as IPAudio

        waveform = self.waveform.select_by_ms(start_ms, end_ms)

        return IPAudio(data=waveform.data, rate=waveform.sample_rate)

    def select_waveform(
        self, start_ms: float | None, end_ms: float | None = None
    ) -> np.ndarray:
        return self.waveform[start_ms:end_ms]

    def add_token(
        self,
        text: str,
        start_ms: int | None = None,
        end_ms: int | None = None,
        follow=" ",
    ) -> None:
        if self.tokens is None:
            self.tokens = AudioTokenList()
        if start_ms and end_ms:
            waveform = self.select_waveform(start_ms, end_ms)
        else:
            waveform = None
        self.tokens.append(
            AudioToken(
                start_ms=start_ms,
                end_ms=end_ms,
                text=text,
                waveform=waveform,
                follow=follow,
            )
        )

    def clear(self) -> None:
        self.waveform = None
        self.feats = None
        self.steps = None
        if self.segments:
            for span in self.segments:
                span.waveform = None
                span.feats = None
                span.scores = None
        if self.sents:
            for span in self.sents:
                span.waveform = None
                span.feats = None
                span.scores = None

    def set_waveform(self, data: np.ndarray, sample_rate: int) -> Self:
        self.waveform = Waveform(data=data, sample_rate=sample_rate)
        return self

    def set_text(self, text: str) -> Self:
        self.raw_text = text
        return self

    def __getitem__(self, index) -> Optional[AudioSpan]:
        if not self.segments:
            return None
        return self.segments[index]

    def __len__(self) -> int:
        if not self.segments:
            return 0
        return len(self.segments)


class AudioChannelList(DocList):
    @property
    def text(self):
        """Get the text of all the spans."""
        if not self.sents:
            return ""
        else:
            all_sents = [sent for channel in self for sent in channel.sents]
            sorted_sents = sorted(all_sents, key=lambda x: x.start_ms)
            text = ""
            for sent in sorted_sents:
                text += sent.text
            return text


class Audio(BaseDoc):
    """Audio object that represents an audio file.

    Args:
        url (HttpUrl): URL of the audio file.
        sample_rate (Optional[int], optional): Sample rate of the audio file. Defaults to None.
        waveform (Optional[NdArray], optional): Waveform of the audio file. Defaults to None.
        mono (Optional[bool], optional): Whether the audio file is mono. Defaults to None.
        feats (Optional[NdArray], optional): Features of the audio file. Defaults to None.
        duration (Optional[float], optional): Duration of the audio file. Defaults to None.
        segments (Union[Iterable[List], List], optional): Segments of the audio file. Defaults to None.
        pipeline (List[str], optional): List of processing steps. Defaults to [].
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, extra="ignore"
    )

    url: Union[str, Path] | None = Field(None, description="URL of the audio file.")
    sample_rate: int | None = Field(None, description="Sample rate of the audio file.")
    channels: AudioChannelList[AudioChannel] | None = Field(
        None, description="Channels of the audio file."
    )
    mono: bool | None = Field(None, description="Whether the audio file is mono.")
    duration: float | None = Field(None, description="Duration of the audio file.")
    pipeline: List[str] | None = Field(None, description="List of processing steps.")
    is_bad: bool | None = Field(None, description="Whether the audio file is bad.")
    hotwords: FrozenSet[str] | None = Field(
        None, description="Hotwords of the audio file."
    )
    bad_reason: str | Exception | None = Field(
        None, title="Reason why the audio file is bad."
    )
    bad_component: str | None = Field(
        None, title="Component that marked the audio bad."
    )
    spent_time: Dict[str, float] | None = Field(
        None, title="Time spent on processing the audio."
    )

    @model_validator(mode="after")
    def validate_audio(self):
        if isinstance(self.url, Path):
            self.url = str(
                self.url
            )  # convert Path to str, otherwise it will raise error when saving binary using protobuf protocol
        return self

    def load(self, mono: bool = False) -> "Audio":
        """Load the audio file from the URL."""
        try:
            if Path(self.url).exists():
                data, sample_rate = librosa.load(
                    self.url, sr=self.sample_rate, mono=mono
                )
            else:
                bytes_ = requests.get(self.url).content
                data, sample_rate = librosa.load(
                    BytesIO(bytes_), sr=self.sample_rate, mono=mono
                )
            self.duration = round(librosa.get_duration(y=data, sr=sample_rate), 4)
            self.sample_rate = sample_rate
        except Exception as e:
            raise ValueError(f"Failed to load audio from {self.url}. {e}")
        if len(data.shape) == 1:
            self.mono = True
            self.channels = AudioChannelList[AudioChannel](
                [
                    AudioChannel(
                        id=self.id,
                        waveform=Waveform(
                            data=data, sample_rate=sample_rate, is_normalized=True
                        ),
                    )
                ]
            )

        else:
            self.mono = False
            self.channels = AudioChannelList[AudioChannel](
                [
                    AudioChannel(
                        id=self.id,
                        waveform=Waveform(
                            data=channel_waveform_data,
                            sample_rate=sample_rate,
                            is_normalized=True,
                        ),
                    )
                    for channel_waveform_data in data
                ]
            )
        return self

    def load_example(self, example: Literal["vad", "asr"] = "asr") -> Self:
        vad_example_path = (
            Path(__file__).parent.parent / "asset" / "example" / "vad_example.wav"
        )
        asr_example_path = (
            Path(__file__).parent.parent / "asset" / "example" / "asr_example.wav"
        )
        if example == "vad":
            audio = Audio(url=vad_example_path).load()
            return audio
        elif example == "asr":
            audio = Audio(url=asr_example_path).load()
            return audio
        else:
            raise ValueError(f"Example {example} not found.")

    def load_bytes_io(self, bytes_io: BytesIO) -> Audio:
        """Load the audio file from the BytesIO object.

        Args:
            url (str): URL of the audio file or local path.
            bytes_io (BytesIO): BytesIO object.

        Returns:
            Audio: Audio object.
        """
        assert self.url is not None, "Audio URL is required."
        if self.url[-3:].lower() == "amr" or self.url[-3:].lower() == "m4a":
            audio: AudioSegment = AudioSegment.from_file(
                bytes_io, format=self.url[-3:].lower()
            )
            bytes_io = BytesIO()
            audio.export(bytes_io, format="wav")
        if not any(
            audio_format in self.url.lower()
            for audio_format in (".mp3", ".wav", ".amr", ".m4a")
        ):
            audio: AudioSegment = AudioSegment.from_file(bytes_io)
            bytes_io = BytesIO()
            audio.export(bytes_io, format="wav")
        try:
            arr, sr = librosa.load(bytes_io, sr=self.sample_rate, mono=self.mono)
        except Exception as e:
            logger.warning(f"librosa load failed: {e}, using pydub instead.")
            audio = AudioSegment.from_file(bytes_io)
            bytes_io = BytesIO()
            audio.export(bytes_io, format="wav")
            arr, sr = librosa.load(bytes_io, sr=self.sample_rate, mono=self.mono)
        if len(arr.shape) == 1:
            self.mono = True
            self.channels = AudioChannelList[AudioChannel](
                [
                    AudioChannel(
                        id=self.id,
                        waveform=Waveform(data=arr, sample_rate=sr, is_normalized=True),
                    )
                ]
            )
        else:
            self.mono = False
            self.channels = AudioChannelList[AudioChannel](
                [
                    AudioChannel(
                        id=self.id,
                        waveform=Waveform(
                            data=channel_waveform_data,
                            sample_rate=sr,
                            is_normalized=True,
                        ),
                        sample_rate=self.sample_rate,
                    )
                    for channel_waveform_data in arr
                ]
            )

        self.duration = librosa.get_duration(y=arr, sr=sr)
        return self

    def resample(self, sample_rate: int) -> "Audio":
        """Resample the audio file to the target sample rate.

        Args:
            sample_rate (int): Target sample rate.
        """
        if self.channels is not None:
            self.resample_channel(sample_rate)
        return self

    def resample_channel(self, sample_rate: int) -> "Audio":
        """Resample the audio channel waveform to the target sample rate.

        Args:
            sample_rate (int): Target sample rate.
        """
        if self.channels is None:
            logger.warning(
                f"Audio {self.id} resample failed because it has no channels."
            )
            return self
        for channel in self.channels:
            channel: AudioChannel
            channel.resample(sample_rate)
        return self

    def append_channel(self, channel: AudioChannel | None = None) -> "Audio":
        """Append a channel to the audio file.

        Args:
            channel (AudioChannel): Channel to append.
        """
        if self.channels is None:
            self.channels = AudioChannelList[AudioChannel]()
        if channel is None:
            channel = AudioChannel()
        self.channels.append(channel)
        return self

    def align_channel_bad(self):
        """Align the bad status of the audio file with its channels."""
        if self.channels is None:
            return
        for channel in self.channels:
            if channel.is_bad:
                self.is_bad = True
                self.bad_reason = channel.bad_reason
                self.bad_component = channel.bad_component
                break

    def align_segment_bad(self):
        """Align the bad status of the audio file with its channels."""
        if self.channels is None:
            return
        for channel in self.channels:
            for span in channel.segments:
                if span.is_bad:
                    self.is_bad = True
                    self.bad_reason = span.bad_reason
                    self.bad_component = span.bad_component
                    break

    def clear(self, clear_text: bool = False) -> None:
        """Clear the waveform, features, and scores of the audio file. should be called after processing. this method is used to save memory.

        Args:
            clear_text
        """
        self.clear_waveform()
        if clear_text:
            self.clear_text()
        return self

    def clear_waveform(self) -> "Audio":
        """clear all waveform data"""
        if self.channels is not None:
            for channel in self.channels:
                channel: AudioChannel
                channel.waveform = None
                if channel.segments is not None:
                    for segment in channel.segments:
                        segment: AudioSpan
                        segment.waveform = None
        return self

    def clear_text(self) -> "Audio":
        """Clear the text of the audio file.

        Returns:
            Audio: Audio object.
        """
        if self.channels is not None:
            for channel in self.channels:
                channel: AudioChannel
                channel.raw_text = None
                channel.tokens = None
                channel.segments = None
                channel.sents = None
        return self

    def clear_bad(self) -> "Audio":
        """Clear the bad status of the audio file.

        Returns:
            Audio: Audio object.
        """
        self.is_bad = None
        self.bad_reason = None
        self.bad_component = None
        return self

    def chunk(self, chunk_size_ms: int) -> AudioChunkList:
        """Chunk the audio file into smaller chunks.
        Args:
            chunk_size_ms (int): Size of the chunk in milliseconds.
        Returns:
            AudioList: Chunked audio list.
        """
        if self.channels is None or len(self.channels) == 0:
            raise ValueError("Cannot chunk audio without channels.")
        chunked_audios = AudioChunkList()
        chunk_stride = self.channels[0].waveform.sample_rate / 1000 * chunk_size_ms
        num_chunks = num_chunks = int(np.ceil(self.duration_ms / chunk_size_ms))
        if self.duration_ms > chunk_size_ms:
            for i in range(num_chunks):
                start = int(i * chunk_stride)
                end = int((i + 1) * chunk_stride) if i < num_chunks - 1 else None
                is_start = i == 0
                is_last = i == num_chunks - 1
                chunk_audio = AudioChunk(
                    stream_id=self.id,
                    is_last=is_last,
                    is_start=is_start,
                    waveform=self.channels[0].waveform[start:end],
                )
                chunked_audios.append(chunk_audio)
        else:
            chunk_audio = AudioChunk(
                stream_id=self.id,
                is_last=True,
                waveform=self.channels[0].waveform,
                is_start=True,
            )
            chunked_audios.append(chunk_audio)
        return chunked_audios

    def split_into_spans(self, span_duration_ms: int) -> "AudioSpanList[AudioSpan]":
        """Split the audio file into smaller spans.

        Args:
            span_duration_ms (int): Duration of the span in milliseconds.

        Returns:
            AudioSpanList[AudioSpan]: List of spans.
        """
        chunked_audios = AudioSpanList()
        chunk_stride = self.sample_rate / 1000 * span_duration_ms
        num_chunks = int(np.ceil(self.duration_ms / span_duration_ms))
        if self.duration_ms > span_duration_ms:
            for i in range(num_chunks):
                start = int(i * chunk_stride)
                start_ms = i * span_duration_ms
                end = int((i + 1) * chunk_stride) if i < num_chunks - 1 else None
                if end is not None:
                    end_ms = (i + 1) * span_duration_ms
                else:
                    end_ms = self.duration_ms
                is_last = i == num_chunks - 1
                if self[0].waveform is not None:
                    audio_chunk_waveform = self[0].waveform[start:end]
                else:
                    audio_chunk_waveform = None
                chunk_audio = AudioSpan(
                    id=self.id,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    waveform=audio_chunk_waveform,
                    sample_rate=self.sample_rate,
                    duration=span_duration_ms / 1000,
                    is_last=is_last,
                )
                chunked_audios.append(chunk_audio)
        else:
            chunked_audios.append(self)
        return chunked_audios

    def display(self, channel_idx: int = 0):
        """Display the audio file."""
        from IPython.display import Audio as IPAudio

        return IPAudio(
            data=self.channels[channel_idx].waveform.data,
            rate=self.channels[channel_idx].waveform.sample_rate,
        )

    def set_hotwords(self, hotwords: List[str]) -> "Audio":
        """Set the hotwords of the audio file.

        Args:
            hotwords (List[str]): List of hotwords.
        """
        self.hotwords = frozenset(hotwords)
        return self

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        protocol: Literal[
            "protobuf", "pickle", "json", "json-array", "protobuf-array", "pickle-array"
        ] = "protobuf",
        compress: str | None = None,
    ):
        doc = super().from_bytes(data=data, protocol=protocol, compress=compress)
        return doc

    def from_audio_bytes(self, audio_bytes: bytes) -> "Audio":
        """Create an Audio object from audio bytes.

        Args:
            audio_bytes (bytes): Audio bytes.

        Returns:
            Audio: Audio object.
        """
        bytes_io = BytesIO(audio_bytes)
        audio = AudioSegment.from_file(bytes_io)
        bytes_io = BytesIO()
        audio.export(bytes_io, format="wav")
        arr, sr = librosa.load(bytes_io, sr=self.sample_rate, mono=self.mono)
        if len(arr.shape) == 1:
            self.mono = True
            self.channels = AudioChannelList[AudioChannel](
                [
                    AudioChannel(
                        id=self.id,
                        waveform=Waveform(data=arr, sample_rate=sr, is_normalized=True),
                    )
                ]
            )
        else:
            self.mono = False
            self.channels = AudioChannelList[AudioChannel](
                [
                    AudioChannel(
                        id=self.id,
                        waveform=Waveform(
                            data=channel_waveform_data,
                            sample_rate=sr,
                            is_normalized=True,
                        ),
                        sample_rate=self.sample_rate,
                    )
                    for channel_waveform_data in arr
                ]
            )

        self.duration = librosa.get_duration(y=arr, sr=sr)
        return self

    def from_b64_str(self, b64_str: str) -> "Audio":
        """Create an Audio object from a base64 encoded string.

        Args:
            b64_str (str): Base64 encoded string of the audio file.

        Returns:
            Audio: Audio object.
        """
        import base64

        audio_bytes = base64.b64decode(b64_str.encode("utf-8"))
        return self.from_audio_bytes(audio_bytes)

    @property
    def is_loaded(self):
        if self.channels is None:
            return False
        if len(self.channels) == 0:
            return False
        for channel in self.channels:
            if channel.waveform is None:
                return False
        return True

    @property
    def duration_s(self):
        """Get the duration of the audio file in seconds."""
        if self.duration is not None:
            return self.duration
        if self.channels is None:
            return 0
        if len(self.channels) == 0:
            return 0
        return round(
            len(self.channels[0].waveform.data) / self.channels[0].waveform.sample_rate,
            4,
        )

    @property
    def duration_ms(self):
        """Get the duration of the audio file in milliseconds."""
        return self.duration_s * 1000

    @property
    def audio_format(self) -> str | None:
        if self.url is None:
            return None
        formats = [
            ".mp3",
            ".wav",
            ".amr",
            ".m4a",
            ".flac",
            ".ogg",
            ".opus",
            ".webm",
            ".aac",
            ".wma",
        ]
        for format in formats:
            if format in self.url.lower():
                return format.replace(".", "")
        return None

    def __getitem__(self, idx) -> AudioChannel | None:
        if self.channels is None:
            return None
        return self.channels[idx]

    def __len__(self) -> int:
        if self.channels is None:
            return 0
        return len(self.channels)


class AudioList(DocList):
    def load_stream(self, num_threads: int = -1) -> Iterable[Audio]:
        """Load all the audio files in parallel.

        Args:
            num_threads (int, optional): Number of threads to use. Defaults to -1. If -1, use all available cores.
        """
        if len(self) == 0:
            return
        if num_threads == -1:
            num_threads = get_cpu_cores()
        batch_size = max(len(self) // num_threads, 1)
        res = Parallel(
            n_jobs=num_threads,
            prefer="threads",
            batch_size=batch_size,
            return_as="generator_unordered",
            pre_dispatch="4 * n_jobs",
        )(delayed(doc.load)() for doc in self)
        return res

    def load(self, num_workers: int = 2):
        """Load all the audio files in parallel.

        Args:
            num_workers (int, optional): Number of workers to use. Defaults to -1. If -1, use all available cores.
        """
        if len(self) == 0:
            return
        if num_workers == -1:
            num_workers = get_cpu_cores()
        batch_size = max(len(self) // num_workers, 1)
        _ = Parallel(n_jobs=num_workers, prefer="threads", batch_size=batch_size)(
            delayed(doc.load)() for doc in self
        )
        return self

    @classmethod
    def from_urls(
        cls, urls: Union[str, List[str]], load: bool = False, num_workers: int = 2
    ):
        """Create an AudioList from a list of URLs.

        Args:
            urls (List[str]): List of URLs.
            load (bool, optional): Whether to load the audio files. Defaults to False.
            num_workers (int, optional): Number of workers to use. Defaults to -1. If -1, use all available cores.

        Returns:
            AudioList: List of Audio objects.
        """
        if isinstance(urls, str):
            urls = [urls]
        audios = cls([Audio(url=url) for url in urls])
        if load:
            audios = audios.load(num_workers=num_workers)
        return audios

    def resample_channel(self, sample_rate: int, num_workers: int = 2):
        """Resample all the audio files in parallel.

        Args:
            sample_rate (int): Target sample rate.
            num_workers (int, optional): Number of workers to use. Defaults to -1. If -1, use all available cores.
        """
        if num_workers == -1:
            num_workers = get_cpu_cores()
        batch_size = max(len(self) // num_workers, 1)
        _ = Parallel(n_jobs=num_workers, prefer="threads", batch_size=batch_size)(
            delayed(doc.resample_channel)(sample_rate) for doc in self
        )
        return self

    def filter_audio_id(self, ids: List[str], op: str = "$in") -> Optional["AudioList"]:
        """Filter the audio files by their IDs.
        Args:
            ids (List[str]): List of audio IDs.
            op (str, optional): Operator to use. Defaults to "$in". Can be "$in", "$nin"

        Returns:
            Optional[AudioList]: Filtered audio files.
        """
        query = {"id": {op: ids}}
        audios: AudioList[Audio] = AudioList[Audio](filter_docs(self, query=query))
        return audios

    def filter_urls(self, urls: List[str], op: str = "$in") -> Optional["AudioList"]:
        """Filter the audio files by their URLs.
        Args:
            urls (List[str]): List of audio URLs.
            op (str, optional): Operator to use. Defaults to "$in". Can be "$in", "$nin"

        Returns:
            Optional[AudioList]: Filtered audio files.
        """
        query = {"url": {op: urls}}
        audios: AudioList = filter_docs(self, query=query)
        if len(audios) == 0:
            return None
        return audios

    def analysis_timer(self):
        """Print the time spent on processing the audio files."""
        component_spent = {}
        for audio in self:
            for component, spent in audio.spent_time.items():
                if component not in component_spent:
                    component_spent[component] = 0
                component_spent[component] += spent
        total_spent = sum(component_spent.values())
        print("Total spent time: ", round(total_spent, 2))
        for component, spent in component_spent.items():
            print(f"{component}: {spent:.2f}s, {spent / total_spent:.2%}")

    def clear(self) -> None:
        """Clear the waveform, features, and scores of all the audio files. should be called after processing. this method is used to save memory."""
        for audio in self:
            audio.clear()

    def has_bad_audio(self) -> bool:
        """Check if there is bad audio in the list"""
        ids = [audio.id for audio in self if audio.is_bad]
        return len(ids) > 0

    def save_binary(
        self,
        file: str | Path,
        protocol: Literal[
            "protobuf", "pickle", "json", "json-array", "protobuf-array", "pickle-array"
        ] = "pickle",
        compress: Literal["lz4", "bz2", "lzma", "zlib", "gzip"] | None = None,
        show_progress: bool = False,
    ) -> None:
        """Save the audio list to a binary file.

        Args:
            file (str | Path): Path to the binary file.
            protocol (Literal[ &quot;protobuf&quot;, &quot;pickle&quot;, &quot;json&quot;, &quot;json, optional): the protocol to use. Defaults to &quot;pickle&quot;.
            compress (Literal[&quot;lz4&quot;, &quot;bz2&quot;, &quot;lzma&quot;, &quot;zlib&quot;, &quot;gzip&quot;] | None, optional): the compression method to use. Defaults to None.
            show_progress (bool, optional): Whether to show the progress bar. Defaults to False.
        """
        return super().save_binary(file, protocol, compress, show_progress)

    @classmethod
    def load_binary(
        cls,
        file: str | bytes | Path,
        protocol: Literal[
            "protobuf", "pickle", "json", "json-array", "protobuf-array", "pickle-array"
        ] = "pickle",
        compress: Literal["lz4", "bz2", "lzma", "zlib", "gzip"] | None = None,
        show_progress: bool = False,
        streaming: bool = False,
    ) -> DocList[Audio] | Generator[Any, None, None]:
        """Load the audio list from a binary file.

        Args:
            file (str | Path): Path to the binary file.
            show_progress (bool, optional): Whether to show the progress bar. Defaults to False.
            streaming (bool, optional): Whether to stream the data. Defaults to False.
            protocol (Literal[ &quot;protobuf&quot;, &quot;pickle&quot;, &quot;json&quot;, &quot;json, optional): the protocol to use. Defaults to &quot;pickle&quot;.
            compress (Literal[&quot;lz4&quot;, &quot;bz2&quot;, &quot;lzma&quot;, &quot;zlib&quot;, &quot;gzip&quot;] | None, optional): the compression method to use. Defaults to None.

        Returns:
            AudioList: Audio list.
        """
        docs = DocList[Audio].load_binary(
            file=file,
            protocol=protocol,
            compress=compress,
            show_progress=show_progress,
            streaming=streaming,
        )
        if isinstance(docs, Generator):
            return docs
        return AudioList[Audio](docs)

    def copy(self) -> "AudioList":
        docs = [audio.model_copy(deep=True) for audio in self]
        return AudioList[Audio](docs)

    def clear(self, clear_text: bool = False) -> "AudioList":  # noqa
        for audio in self:
            audio: Audio
            audio.clear(clear_text=clear_text)
        return self

    def clear_waveform(self) -> "AudioList":
        for audio in self:
            audio: Audio
            audio.clear_waveform()
        return self

    def clear_text(self) -> "AudioList":
        for audio in self:
            audio: Audio
            audio.clear_text()
        return self

    def group_by_hotwords(self) -> Dict[FrozenSet[str], "AudioList"]:
        """Group the audio files by their hotwords. used for batch processing."""
        groups = {}
        for audio in self:
            hotwords = audio.hotwords
            if hotwords is None:
                hotwords = frozenset()
            if hotwords not in groups:
                groups[hotwords] = AudioList()
            groups[hotwords].append(audio)
        return groups

    def shuffle(self) -> "AudioList":
        """Shuffle the audio files."""
        import random

        random.shuffle(self)
        return self

    def to_dataset(
        self,
        dataset_dir: str | Path,
        num_workers: int = 2,
        mode: Literal["overwrite", "append"] = "overwrite",
        chunk_bytes: str = "60MB",
    ):
        """Convert the audio list to a litdata format streamdataset.
        Args:
            dataset_dir (str | Path): Path to the dataset directory.
            num_workers (int, optional): Number of workers to use. Defaults to 2.
            mode (Literal[&quot;overwrite&quot;, &quot;append&quot;], optional): Whether to overwrite the dataset or append to it. Defaults to &quot;overwrite&quot;.
            chunk_bytes (str, optional): Chunk size. Defaults to &quot;60MB&quot;.
        Returns:
            AudioDataset: Dataset.
        """
        from litdata import optimize

        def get_item(index: int) -> Dict[str, Any]:
            audio = self[index]
            item = {
                "sample_rate": audio.sample_rate,
                "data": audio[0].waveform.data,
                "text": audio[0].text,
            }
            return item

        optimize(
            fn=get_item,
            inputs=list(range(len(self))),
            output_dir=dataset_dir,
            num_workers=num_workers,
            chunk_bytes=chunk_bytes,
            mode=mode,
        )

    @classmethod
    def from_dataset(cls, dataset_dir: str | Path) -> AudioList:
        """load litdata streamdataset to AudioList"""
        from litdata import StreamingDataset

        ds = StreamingDataset(input_dir=dataset_dir)
        audios = AudioList()
        for item in ds:
            sample_rate = item.get("sample_rate", None) or item.get("sr", None)
            audio = Audio(sample_rate=sample_rate).append_channel()
            audio[0].waveform = Waveform(sample_rate=sample_rate, data=item["data"])
            audio[0].text = item["text"]
            audios.append(audio)
        return audios

    @property
    def duration_s(self):
        """Get the total duration of all the audio files in seconds."""
        durations = []
        for i in range(len(self)):
            audio: Audio = self[i]
            if audio.duration is not None:
                durations.append(audio.duration)
            else:
                durations.append(audio.duration_s)
        return round(sum(durations), 4)

    @property
    def duration_ms(self):
        """Get the total duration of all the audio files in milliseconds."""
        durations = []
        for audio in self:
            if audio.duration_ms is not None:
                durations.append(audio.duration_ms)
        return round(sum(durations), 4)

    @property
    def channels(self):
        """Get all the channels of the audio files."""
        channels = []
        for audio in self:
            if audio.channels is not None:
                channels.extend(audio.channels)
        return channels

    @property
    def bad_audios(self) -> "AudioList":
        """Get the bad audios in the list"""
        return AudioList([audio for audio in self if audio.is_bad])

    @property
    def good_audios(self) -> "AudioList":
        """Get the good audios in the list"""
        return AudioList([audio for audio in self if not audio.is_bad])

    def __sub__(self, other: "AudioList") -> "AudioList":
        """Get the difference between two AudioList objects."""
        other_ids = [audio.id for audio in other]
        return self.filter_audio_id(other_ids, op="$nin")

    def __str__(self) -> str:
        num_bad_audios = [audio.is_bad for audio in self].count(True)
        return f"AudioList with {len(self)} audios, {num_bad_audios} bad audios."

    def __repr__(self) -> str:
        return self.__str__()


@lru_cache
def get_cpu_cores():
    return os.cpu_count()


class AudioChunk(BaseDoc):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    id: ID = None
    stream_id: ID
    waveform: Waveform
    start_ms: int | None = None
    end_ms: int | None = None
    tokens: AudioTokenList[AudioToken] | None = None
    is_start: bool = False
    is_last: bool = False
    vad_state: Literal["segment_start", "segment_end", "segment_mid"] | None = None

    @property
    def text(self) -> str:
        """Get the text of the audio chunk."""
        if self.tokens is None:
            return ""
        text = ""
        for token in self.tokens:
            text += token.text
        return text

    @property
    def is_final(self) -> bool:
        """Get the is_final of the audio chunk."""
        return self.is_last

    @property
    def duration_ms(self) -> float:
        """Get the duration of the audio chunk in milliseconds."""
        return self.waveform.duration_ms

    @property
    def duration_s(self) -> float:
        """Get the duration of the audio chunk in seconds."""
        return self.waveform.duration_s

    def clear(self) -> "AudioChunk":
        self.waveform = None
        self.tokens = None
        return self

    def display(self):
        """Display the audio chunk."""
        from IPython.display import Audio as IPAudio

        return IPAudio(data=self.waveform.data, rate=self.waveform.sample_rate)


class AudioChunkList(DocList):
    def concat(self) -> Audio:
        """Concatenate all the audio chunks into a single audio file."""
        if len(self) == 0:
            return Audio()
        waveform = Waveform.concatenate([chunk.waveform for chunk in self])
        audio = Audio(sample_rate=waveform.sample_rate)
        audio.append_channel(AudioChannel(waveform=waveform))
        return audio

    def concat_to_chunk(self) -> AudioChunk:
        """Concatenate all the audio chunks into a single audio chunk.

        note: this method will set start_ms, end_ms, and stream_id of the audio chunk.
        if there is only one audio chunk, return the audio chunk directly.
        if there are multiple audio chunks, return a new audio chunk with concatenated waveform.
        if there are no audio chunks, return an empty audio chunk.
        """
        if len(self) == 0:
            return AudioChunk()
        if len(self) == 1:
            return self[0]
        stream_id = self[0].stream_id
        start_ms = self[0].start_ms
        end_ms = self[-1].end_ms
        waveform = Waveform.concatenate([chunk.waveform for chunk in self])
        audio_chunk = AudioChunk(
            waveform=waveform, start_ms=start_ms, end_ms=end_ms, stream_id=stream_id
        )
        return audio_chunk

    def concat_to_audio(self) -> Audio:
        """Concatenate all the audio chunks into a single audio file.
        note: this method will set the is_last property of the audio chunk.
        """
        if len(self) == 0:
            return Audio()
        if len(self) == 1:
            self[0].is_last = True
            return self[0].concat()
        waveform = Waveform.concatenate([chunk.waveform for chunk in self])
        audio = Audio(sample_rate=waveform.sample_rate)
        audio.append_channel(AudioChannel(waveform=waveform))
        return audio
