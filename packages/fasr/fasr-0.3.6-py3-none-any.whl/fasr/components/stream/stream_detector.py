from fasr.data import AudioChunk
from fasr.config import registry
from typing_extensions import Self
from fasr.models.stream_vad.base import StreamVADModel
from pydantic import Field, validate_call
from .base import BaseStreamComponent


@registry.stream_components.register("stream_detector")
class StreamVoiceDetector(BaseStreamComponent):
    name: str = "stream_detector"

    model: StreamVADModel | None = Field(
        None, description="The vad model to use for voice detection"
    )

    def predict(self, audio_chunk: AudioChunk) -> AudioChunk:
        state = self.get_state(stream_id=audio_chunk.stream_id)
        segments = self.model.detect_chunk(
            waveform=audio_chunk.waveform, is_last=audio_chunk.is_last, state=state
        )
        audio_chunk.segments = segments
        if audio_chunk.is_last:
            self.clear_state(stream_id=audio_chunk.stream_id)
        return audio_chunk

    @validate_call
    def setup(
        self,
        model: str = "stream_fsmn",
        **kwargs,
    ) -> Self:
        model: StreamVADModel = registry.stream_vad_models.get(model)()
        self.model = model.from_checkpoint(**kwargs)
        return self
