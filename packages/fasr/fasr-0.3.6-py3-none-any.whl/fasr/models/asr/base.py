from fasr.models.base import Model
from fasr.data import AudioTokenList
from typing import List
from abc import abstractmethod
import numpy as np
import torch


class ASRModel(Model):
    """语音识别模型基类"""

    @abstractmethod
    def transcribe(
        self,
        batch: List[np.ndarray] | List[torch.Tensor],
        **kwargs,
    ) -> List[AudioTokenList]:
        raise NotImplementedError
