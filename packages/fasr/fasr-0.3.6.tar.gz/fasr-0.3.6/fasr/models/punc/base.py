from fasr.models.base import Model
from fasr.data import AudioSpan
from typing import List
from abc import abstractmethod


class PuncModel(Model):
    @abstractmethod
    def restore(self, text: str) -> List[AudioSpan]:
        raise NotImplementedError
