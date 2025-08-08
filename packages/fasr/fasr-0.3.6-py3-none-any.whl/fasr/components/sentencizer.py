from .base import BaseComponent
from fasr.data.audio import (
    AudioChannel,
    AudioList,
    Audio,
)
from fasr.config import registry
from joblib import Parallel, delayed
from fasr.models.punc.base import PuncModel
from typing_extensions import Self


@registry.components.register("sentencizer")
class SpeechSentencizer(BaseComponent):
    """句子分割器"""

    name: str = "sentencizer"

    model: PuncModel | None = None
    num_threads: int = 1

    def predict(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        channels = []
        for audio in audios:
            if audio.channels is not None:
                channels.extend(audio.channels)
        _ = Parallel(n_jobs=self.num_threads, prefer="threads")(
            delayed(self.predict_channel)(channel) for channel in channels
        )
        return audios

    def predict_channel(self, channel: AudioChannel) -> AudioChannel:
        text = channel.text
        if text.strip() != "":
            sents = self.model.restore(text=text)
            channel.sents = sents
            sent_tokens = []
            seg_tokens = []
            if channel.segments is not None:
                for seg in channel.segments:
                    seg_tokens.extend(seg.tokens)
            for sent in channel.sents:
                sent_tokens.extend(sent.tokens)
            if len(seg_tokens) == len(sent_tokens):
                for sent_token, seg_token in zip(sent_tokens, seg_tokens):
                    if sent_token.text == seg_token.text:
                        sent_token.start_ms = seg_token.start_ms
                        sent_token.end_ms = seg_token.end_ms
            for sent in sents:
                sent.start_ms = sent.tokens[0].start_ms
                sent.end_ms = sent.tokens[-1].end_ms
        return channel

    def setup(
        self,
        num_threads: int = 1,
        model: str = "ct_transformer",
        **kwargs,
    ) -> Self:
        """从funasr模型目录加载组件

        Args:
            num_threads (int, optional): 并行线程数. Defaults to 1.
            model (str, optional): 模型名称. Defaults to "ct_transformer".
        """

        model: PuncModel = registry.punc_models.get(model)()
        self.model = model.from_checkpoint(**kwargs)
        self.num_threads = num_threads
        return self
