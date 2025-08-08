from .base import BaseComponent
from fasr.data.audio import (
    AudioList,
    Audio,
    AudioSpanList,
    AudioSpan,
    AudioToken,
    AudioTokenList,
    AudioChannel,
)
from fasr.config import registry
from fasr.models.asr.base import ASRModel
from typing import List, Iterable
from typing_extensions import Self
from joblib import Parallel, delayed
from pydantic import validate_call


@registry.components.register("recognizer")
class SpeechRecognizer(BaseComponent):
    name: str = "recognizer"

    model: ASRModel | None = None
    num_threads: int = 1
    batch_size_s: int = 100
    hotwords: frozenset[str] | None = None

    def predict(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        if self.hotwords is not None:
            for audio in audios:
                audio: Audio
                if audio.hotwords is None:
                    audio.set_hotwords(self.hotwords)
        groups = audios.group_by_hotwords()
        _ = Parallel(
            n_jobs=self.num_threads, prefer="threads", pre_dispatch="1 * n_jobs"
        )(
            delayed(self.predict_step)(batch_segments, list(hotwords))
            for hotwords, group_audios in groups.items()
            for batch_segments in self.batch_audio_segments(audios=group_audios)
        )
        return audios

    def predict_step(
        self, batch_segments: List[AudioSpan | AudioChannel], hotwords: List[str] = []
    ) -> List[AudioSpan | AudioChannel]:
        batch_waveforms = [seg.waveform for seg in batch_segments]
        sample_rate = batch_waveforms[0].sample_rate  # 一个batch的音频片段采样率相同
        batch_data = [waveform.data for waveform in batch_waveforms]
        batch_tokens = self.model.transcribe(
            batch=batch_data, sample_rate=sample_rate, hotwords=hotwords
        )
        for seg, tokens in zip(batch_segments, batch_tokens):
            if not isinstance(seg, AudioChannel):
                if seg.start_ms is not None and seg.end_ms is not None:
                    for token in tokens:
                        token: AudioToken
                        if (
                            token.start_ms and token.end_ms
                        ):  # not all asr model predict timestamp
                            token.start_ms += seg.start_ms
                            token.end_ms += seg.start_ms
            seg.tokens = AudioTokenList(docs=tokens)
        return batch_segments

    def batch_audio_segments(
        self, audios: AudioList[Audio]
    ) -> Iterable[AudioSpanList[AudioSpan]]:
        """将音频片段组成批次。
        步骤：
        - 1. 将音频片段按照时长排序。
        - 2. 将音频片段按照时长分组，每组时长不超过batch_size_s。
        """
        all_segments = []
        for audio in audios:
            if not audio.is_bad:
                for channel in audio.channels:
                    if channel.segments is None:  # 兼容没有vad模型的情况
                        all_segments.append(channel)
                    else:
                        for seg in channel.segments:
                            all_segments.append(seg)
        return self.batch_segments(all_segments)

    def batch_segments(
        self, segments: Iterable[AudioSpan]
    ) -> Iterable[AudioSpanList[AudioSpan]]:
        """将音频片段组成批次。"""
        batch_size_ms = self.batch_size_s * 1000
        segments = [seg for seg in segments]
        sorted_segments = self.sort_segments(segments)
        batch = AudioSpanList()
        for seg in sorted_segments:
            max_duration_ms = max(batch.max_duration_ms, seg.duration_ms)
            current_batch_duration_ms = max_duration_ms * (
                len(batch) + 1
            )  # 如果加入当前片段，是否超过batch_size_s
            if current_batch_duration_ms > batch_size_ms:
                yield batch
                batch = AudioSpanList()
                batch.append(seg)
            else:
                batch.append(seg)
        if len(batch) > 0:
            yield batch

    def sort_segments(
        self, segments: List[AudioSpan | AudioChannel]
    ) -> List[AudioSpan | AudioChannel]:
        return sorted(segments, key=lambda x: x.duration_ms)

    @validate_call
    def setup(
        self,
        model: str = "paraformer",
        batch_size_s: int = 100,
        num_threads: int = 1,
        hotwords: Iterable[str] | None = None,
        **kwargs,
    ) -> Self:
        model: ASRModel = registry.asr_models.get(model)()
        self.model = model.from_checkpoint(**kwargs)
        self.num_threads = num_threads
        self.batch_size_s = batch_size_s
        self.hotwords = frozenset(hotwords) if hotwords is not None else None
        return self
