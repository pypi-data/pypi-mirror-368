from typing_extensions import Self
from typing import List
from pathlib import Path

from funasr import AutoModel
import numpy as np
import torch

from fasr.config import registry
from fasr.data import AudioToken, AudioTokenList
from .base import ASRModel


@registry.asr_models.register("paraformer")
class ParaformerForASR(ASRModel):
    checkpoint: str = "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
    endpoint: str = "modelscope"

    paraformer: AutoModel | None = None

    def transcribe(
        self, batch: List[np.ndarray | torch.Tensor], **kwargs
    ) -> List[List[AudioToken]]:
        fs = kwargs.get("sample_rate", 16000)
        results = self.paraformer.generate(input=batch, fs=fs)
        batch_tokens = []
        for result in results:
            tokens = AudioTokenList()
            result_text = result["text"]
            if result_text:
                texts = result["text"].split(" ")
                timestamps = result["timestamp"]
                assert len(texts) == len(timestamps), (
                    f"Texts and timestamps have different lengths: {len(texts)} != {len(timestamps)}"
                )
                for token_text, timestamp in zip(texts, timestamps):
                    start_ms = timestamp[0]
                    end_ms = timestamp[1]
                    token = AudioToken(
                        start_ms=start_ms, end_ms=end_ms, text=token_text
                    )
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
        self.paraformer = model
        self.paraformer.kwargs["batch_size"] = 10000  # enable batch processing
        return self

    def get_config(self):
        raise NotImplementedError

    def load(self, save_dir, **kwargs):
        raise NotImplementedError

    def save(self, save_dir, **kwargs):
        raise NotImplementedError
