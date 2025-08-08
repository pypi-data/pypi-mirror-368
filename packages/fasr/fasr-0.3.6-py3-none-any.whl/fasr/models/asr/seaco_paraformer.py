from .base import ASRModel
from typing_extensions import Self
from typing import List
from funasr import AutoModel
from fasr.config import registry
from fasr.data import AudioToken, AudioTokenList
from pathlib import Path
import numpy as np
import torch


@registry.asr_models.register("seaco_paraformer")
class SeacoParaformerForASR(ASRModel):
    checkpoint: str = (
        "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
    )
    endpoint: str = "modelscope"

    seaco_paraformer: AutoModel | None = None

    def transcribe(
        self, batch: List[np.ndarray | torch.Tensor], **kwargs
    ) -> List[List[AudioToken]]:
        fs = kwargs.get("sample_rate", 16000)
        hotwords = kwargs.get("hotwords", None)
        hotword = " ".join(hotwords) if hotwords else None
        results = self.seaco_paraformer.generate(input=batch, fs=fs, hotword=hotword)
        batch_tokens = []
        for result in results:
            tokens = AudioTokenList()
            result_text = result["text"]
            if result_text:
                texts = result["text"].split(" ")
            else:
                texts = []
            timestamps = result["timestamp"]
            assert len(texts) == len(timestamps), (
                f"Texts and timestamps have different lengths: {len(texts)} != {len(timestamps)}"
            )
            for token_text, timestamp in zip(texts, timestamps):
                start_ms = timestamp[0]
                end_ms = timestamp[1]
                token = AudioToken(start_ms=start_ms, end_ms=end_ms, text=token_text)
                assert token.end_ms - token.start_ms > 0, f"{token}"
                tokens.append(token)
            batch_tokens.append(tokens)
        return batch_tokens

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        disable_update: bool = True,
        disable_log: bool = True,
        disable_pbar: bool = True,
        **kwargs,
    ) -> Self:
        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")
        model = AutoModel(
            model=checkpoint_dir,
            disable_update=disable_update,
            disable_log=disable_log,
            disable_pbar=disable_pbar,
            **kwargs,
        )
        self.seaco_paraformer = model
        self.seaco_paraformer.model.generate_hotwords_list = self.generate_hotwords
        self.seaco_paraformer.kwargs["batch_size"] = 10000  # enable batch processing
        return self

    def generate_hotwords(
        self, hotword_list_or_file: str | None = None, **kwargs
    ) -> List[List[int]] | None:
        """Generate hotwords list.

        Args:
            hotword_list_or_file (str): Hotword string. e.g. "你好 你好吗"
        """
        if not hotword_list_or_file:
            return None
        hotwords = hotword_list_or_file.strip().split(" ")
        if len(hotwords) == 0:
            return None
        all_ids = []
        for hotword in hotwords:
            tokens = [
                s for s in hotword
            ]  # todo: better tokenization. now it's just char-level.
            all_ids.append(self.tokens2ids(tokens))
        all_ids.append(self.tokens2ids(["<s>"]))
        return all_ids

    def tokens2ids(self, tokens: List[AudioToken], **kwargs) -> List[int]:
        return self.tokenizer.tokens2ids(tokens)

    @property
    def tokenizer(self):
        return self.seaco_paraformer.kwargs["tokenizer"]

    def get_config(self):
        raise NotImplementedError

    def load(self, save_dir, **kwargs):
        raise NotImplementedError

    def save(self, save_dir, **kwargs):
        raise NotImplementedError
