from fasr.models.base import Model
from fasr.data import AudioSpan, Waveform
from abc import abstractmethod
from typing import List


class VADModel(Model):
    @abstractmethod
    def detect(self, waveform: Waveform) -> List[AudioSpan]:
        raise NotImplementedError
