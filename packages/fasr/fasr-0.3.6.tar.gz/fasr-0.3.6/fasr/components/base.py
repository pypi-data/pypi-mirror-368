from abc import ABC, abstractmethod
from pydantic import ConfigDict, BaseModel
from fasr.config import Config
from fasr.data.audio import (
    AudioList,
    Audio,
)
from typing import Any, Dict, List, Union
import torch
from fasr.utils.base import IOMixin
from pathlib import Path
from loguru import logger
import traceback


class BaseComponent(IOMixin, BaseModel, ABC):
    """A component is a module that can set tag on audio data"""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)
    timer_data: Dict[str, float] | None = (
        None  # 使用utils.time_it.timer装饰器时，自动记录时间。
    )
    name: str | None = None
    input_tags: List[str] = []
    output_tags: List[str] = []

    @abstractmethod
    def predict(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        raise NotImplementedError

    @abstractmethod
    def setup(
        self, checkpoint_dir: str, device: str = "cpu", compile: bool = False, **kwargs
    ):
        raise NotImplementedError

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

    def _filter_bad_audios(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        """filter bad audios"""
        ids = []
        for audio in audios:
            audio: Audio
            if not audio.is_bad:
                ids.append(audio.id)
        return audios.filter_audio_id(ids)

    def _to_audios(
        self,
        input: Union[str, List[str], Any, Audio, AudioList[Audio], Path, List[Path]],
    ) -> AudioList[Audio]:
        if isinstance(input, str):
            audios = AudioList[Audio].from_urls([input], load=False)
            return audios
        elif isinstance(input, list):
            audios = AudioList()
            for item in input:
                if isinstance(item, str):
                    audio = Audio(url=item)
                    audios.append(audio)
                elif isinstance(item, Audio):
                    audios.append(item)
                elif isinstance(item, Path):
                    audio = Audio(url=item)
                    audios.append(audio)
                else:
                    raise ValueError(
                        f"Invalid item type: {type(item)} for component {self.name}"
                    )
            return audios
        elif isinstance(input, Audio):
            return AudioList[Audio]([input])
        elif isinstance(input, AudioList):
            return input
        elif isinstance(input, Path):
            return AudioList[Audio](docs=[Audio(url=input)])
        else:
            raise ValueError(
                f"Invalid input type: {type(input)} for component {self.name}"
            )

    def __ror__(
        self,
        input: Union[str, List[str], Audio, AudioList],
        *args,
        **kwargs,
    ) -> AudioList[Audio]:
        """组件之间的同步连接符号 `|` 实现"""
        audios = self._to_audios(input=input)
        audios = self._filter_bad_audios(audios)
        for audio in audios:
            audio: Audio
            if audio.pipeline is None:
                audio.pipeline = []
            audio.pipeline.append(self.name)
        try:
            audios = self.predict(audios)
        except Exception as e:
            for audio in audios:
                audio.is_bad = True
                audio.bad_reason = str(e)
                audio.bad_component = self.name
                self.log_component_error(details=traceback.format_exc())
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                current_gpu_index = torch.cuda.current_device()
                available_memory = torch.cuda.get_device_properties(
                    current_gpu_index
                ).total_memory / (1024**3)
                used_memory = torch.cuda.memory_allocated(current_gpu_index) / (1024**3)
                free_memory = available_memory - used_memory
                if free_memory <= 0:
                    raise MemoryError("Out of GPU memory.")
        return audios
