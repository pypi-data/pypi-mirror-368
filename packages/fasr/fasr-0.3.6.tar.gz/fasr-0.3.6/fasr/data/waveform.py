from __future__ import annotations
from docarray import BaseDoc
from docarray.typing import ID, NdArray
from typing_extensions import Self
from pydantic import ConfigDict, Field
import librosa
import numpy as np
from torch import Tensor
from typing import List


class Waveform(BaseDoc):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    id: ID | None = None
    data: np.ndarray | None = Field(None, description="Waveform data.")
    sample_rate: int | None = Field(None, description="Sample rate of the waveform.")
    is_normalized: bool | None = Field(
        None, description="Whether the waveform is normalized."
    )
    feats: NdArray | None = Field(None, description="Features of the waveform.")
    scores: NdArray | None = Field(None, description="scores of the waveform.")

    def resample(self, sample_rate: int) -> Self:
        """Resample the waveform to the target sample rate.

        Args:
            sample_rate (int): Target sample rate.
        """
        self.data = librosa.resample(
            self.data, orig_sr=self.sample_rate, target_sr=sample_rate
        )
        self.sample_rate = sample_rate
        return self

    @classmethod
    def concatenate(cls, waveforms: List[Waveform]) -> Self:
        """Concatenate the waveform with another waveform."""
        data = np.concatenate([waveform.data for waveform in waveforms])
        sample_rate = waveforms[0].sample_rate
        return cls(data=data, sample_rate=sample_rate)

    def append(self, waveform: Waveform) -> Self:
        """Append the waveform with another waveform."""
        assert self.sample_rate == waveform.sample_rate, (
            "Only support the same sample rate."
        )
        data = np.concatenate([self.data, waveform.data])
        self.data = data
        return self

    def flatten(self) -> Self:
        """Flatten the waveform."""
        self.data = self.data.flatten()
        return self

    def as_1d(self, clear: bool = True) -> Self:
        """Flatten the waveform."""
        self.data = self.data.flatten()
        if clear:
            self.feats = None
            self.scores = None
        return self

    def display(self) -> Self:
        """Display the waveform."""
        from IPython.display import Audio

        return Audio(data=self.data, rate=self.sample_rate)

    def select_by_ms(self, start: float | None, end: float | None) -> Waveform:
        """Select the waveform by milliseconds."""
        if start is None:
            start = 0
        if end is None:
            end = self.duration_ms
        start_idx = int(start * self.sample_rate / 1000)
        end_idx = int(end * self.sample_rate / 1000)
        return self[start_idx:end_idx]

    @property
    def ndim(self):
        """Get the number of dimensions of the waveform."""
        if isinstance(self.data, np.ndarray):
            return self.data.ndim
        elif isinstance(self.data, Tensor):
            return self.data.dim()

    @property
    def duration(self):
        """Get the duration of the waveform in seconds."""
        return librosa.get_duration(y=self.data, sr=self.sample_rate)

    @property
    def duration_s(self):
        """Get the duration of the waveform in seconds."""
        return round(librosa.get_duration(y=self.data, sr=self.sample_rate), 3)

    @property
    def duration_ms(self):
        """Get the duration of the waveform in milliseconds."""
        return self.duration * 1000

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index: int | slice) -> Waveform:
        """Get the value at the index. e.g. waveform[0], waveform[1:10]"""
        data = self.data[index]
        return Waveform(data=data, sample_rate=self.sample_rate)
