from fasr.data import AudioList, AudioChannel, Audio
from fasr.config import registry
from typing import List
from typing_extensions import Self
from fasr.components.base import BaseComponent
from joblib import Parallel, delayed
from loguru import logger
from fasr.models.vad.base import VADModel
from pydantic import Field


@registry.components.register("detector")
class VoiceDetector(BaseComponent):
    name: str = "detector"
    input_tags: List[str] = ["audio.channels"]
    output_tags: List[str] = ["channel.segments"]

    model: VADModel | None = Field(
        None, description="The vad model to use for voice detection"
    )
    threshold: float | None = Field(
        None,
        description="The threshold for audio duration, only audios with duration > threshold will be detected",
    )
    num_threads: int | None = Field(
        None, description="The number of threads to use for parallel processing"
    )

    def predict(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        _audios = self.check_audios_threshold(audios)
        all_channels = [channel for audio in _audios for channel in audio.channels]
        batch_size = max(1, len(all_channels) // self.num_threads)
        _ = Parallel(n_jobs=self.num_threads, prefer="threads", batch_size=batch_size)(
            delayed(self.predict_channel)(channel) for channel in all_channels
        )
        return audios

    def predict_channel(self, channel: AudioChannel) -> AudioChannel:
        segments = self.model.detect(waveform=channel.waveform)
        channel.segments = segments
        return channel

    def check_audios_threshold(self, audios: AudioList) -> bool:
        new_audios = AudioList()
        # 大于threshold的音频才进行检测
        if self.threshold is not None:
            for audio in audios:
                if audio.duration > self.threshold:
                    new_audios.append(audio)
                else:
                    logger.warning(
                        f"Audio {audio.id} duration {audio.duration} < threshold {self.threshold}, skip detection"
                    )
        else:
            new_audios = audios
        return new_audios

    def setup(
        self,
        model: str = "fsmn",
        num_threads: int = 1,
        threshold: float = None,
        **kwargs,
    ) -> Self:
        self.model: VADModel = registry.vad_models.get(model)()
        self.model = self.model.from_checkpoint(**kwargs)
        self.num_threads = num_threads
        self.threshold = threshold
        return self
