from fasr.config import Config
from fasr.utils.base import CheckpointMixin, IOMixin
from pathlib import Path
from typing_extensions import Self
from typing import Dict
from pydantic import ConfigDict


class Model(CheckpointMixin, IOMixin):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True
    )

    def get_config(self) -> Config:
        raise NotImplementedError

    def load(self, save_dir: str | Path, **kwargs) -> Self:
        raise NotImplementedError

    def save(self, save_dir: str | Path, **kwargs) -> None:
        raise NotImplementedError

    def from_checkpoint(self, checkpoint_dir: str | Path, **kwargs) -> Self:
        raise NotImplementedError


class StreamModel(Model):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True
    )

    states: Dict = {}

    def reset(self):
        self.states.clear()

    def remove_state(self, key: str):
        self.states.pop(key, None)

    def get_state(self, key: str):
        return self.states.get(key, None)
