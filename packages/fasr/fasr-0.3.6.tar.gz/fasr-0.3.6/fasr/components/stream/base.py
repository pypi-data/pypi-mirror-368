from abc import ABC, abstractmethod
from pydantic import ConfigDict, BaseModel
from fasr.config import Config
from fasr.data import AudioChunk
from typing import Dict
from fasr.utils.base import IOMixin
from loguru import logger
import traceback


class BaseStreamComponent(IOMixin, BaseModel, ABC):
    """A component is a module that can set tag on audio data"""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)
    timer_data: Dict[str, float] | None = (
        None  # 使用utils.time_it.timer装饰器时，自动记录时间。
    )
    name: str | None = None
    states: Dict[str, Dict] = {}

    @abstractmethod
    def predict(self, audio_chunk: AudioChunk) -> AudioChunk:
        raise NotImplementedError

    @abstractmethod
    def setup(
        self, checkpoint_dir: str, device: str = "cpu", compile: bool = False, **kwargs
    ):
        raise NotImplementedError

    def get_state(self, stream_id: str) -> Dict:
        key: str = stream_id
        if key not in self.states:
            self.states[key] = {}
        return self.states[key]

    def clear_state(self, stream_id: str) -> None:
        key: str = stream_id
        if key in self.states:
            del self.states[key]

    def get_config(self) -> Config:
        raise NotImplementedError

    def load(self, save_dir: str):
        raise NotImplementedError

    def save(self, save_dir: str):
        raise NotImplementedError

    def log_component_error(self, details: str = ""):
        logger.error(
            f"Component {self.name} error, details: {details}",
        )

    def __ror__(
        self,
        input: AudioChunk,
        *args,
        **kwargs,
    ) -> AudioChunk:
        """组件之间的同步连接符号 `|` 实现"""
        try:
            audio_chunk = self.predict(audio_chunk=input)
        except Exception as e:
            audio_chunk.is_bad = True
            audio_chunk.bad_reason = str(e)
            audio_chunk.bad_component = self.name
            self.log_component_error(details=traceback.format_exc())
        return audio_chunk
