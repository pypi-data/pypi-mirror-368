from pydantic import ConfigDict
from abc import abstractmethod
import numpy as np
from fasr.utils.base import IOMixin, CheckpointMixin


class BaseWaveformPreprocessor(IOMixin, CheckpointMixin):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True
    )

    @abstractmethod
    def process_waveform(self, waveform: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def from_checkpoint(self, checkpoint_dir: str, **kwargs):
        raise NotImplementedError

    def get_config(self):
        raise NotImplementedError

    def save(self, save_dir):
        raise NotImplementedError

    def load(self, save_dir):
        raise NotImplementedError
