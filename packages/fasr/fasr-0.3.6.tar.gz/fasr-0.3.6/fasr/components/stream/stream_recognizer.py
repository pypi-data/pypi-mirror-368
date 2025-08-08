from .base import BaseStreamComponent
from fasr.data import AudioChunk, AudioSpan, AudioTokenList
from fasr.config import registry
from fasr.models.stream_asr.base import StreamASRModel
from pydantic import validate_call


@registry.stream_components.register("stream_recognizer")
class StreamSpeechRecognizer(BaseStreamComponent):
    name: str = "stream_recognizer"

    model: StreamASRModel | None = None

    def predict(self, audio_chunk: AudioChunk) -> AudioChunk:
        state = self.get_state(stream_id=audio_chunk.stream_id)
        if audio_chunk.segments is None:  # no vad model
            tokens = self.model.transcribe_chunk(
                waveform=audio_chunk.waveform, is_last=audio_chunk.is_last, state=state
            )
            audio_chunk.tokens = tokens
            if audio_chunk.is_last:
                self.clear_state(stream_id=audio_chunk.stream_id)
        else:
            audio_chunk.tokens = AudioTokenList()
            for segment in audio_chunk.segments:
                segment: AudioSpan
                tokens = self.model.transcribe_chunk(
                    waveform=segment.waveform, is_last=segment.is_last, state=state
                )
                segment.tokens = tokens
                audio_chunk.tokens.extend(tokens)
                if segment.is_last:
                    self.clear_state(stream_id=audio_chunk.stream_id)
        return audio_chunk

    @validate_call
    def setup(
        self,
        model: str = "stream_paraformer",
        **kwargs,
    ):
        model: StreamASRModel = registry.stream_asr_models.get(model)()
        self.model = model.from_checkpoint(**kwargs)
        return self
