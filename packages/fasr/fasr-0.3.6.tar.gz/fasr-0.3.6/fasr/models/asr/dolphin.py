from typing_extensions import Self
from typing import List
from pathlib import Path

import torch
import numpy as np
from dolphin.model import DolphinSpeech2Text

from fasr.config import registry
from fasr.data import AudioToken, AudioTokenList
from .base import ASRModel


@registry.asr_models.register("dolphin_small")
class DolphinSmallForASR(ASRModel):
    checkpoint: str = "DataoceanAI/dolphin-small"
    endpoint: str = "hf-mirror"

    dolphin: DolphinSpeech2Text | None = None

    def transcribe(
        self, batch: List[np.ndarray | torch.Tensor], **kwargs
    ) -> List[List[AudioToken]]:
        batch_tokens = []
        for data in batch:
            tokens = AudioTokenList()
            result = self.dolphin(data, predict_time=True)
            # <zh><CN><asr><0.00> 甚至出现交易几乎停滞的情况。<4.20>
            start_time = (
                float(result.text.split("<asr>")[1].split(">")[0].replace("<", ""))
                * 1000
            )
            end_time = (
                float(result.text.split("<asr>")[1].split("<")[2].replace(">", ""))
                * 1000
            )
            tokens.append(
                AudioToken(
                    text=result.text_nospecial, start_ms=start_time, end_ms=end_time
                )
            )
            batch_tokens.append(tokens)
        return batch_tokens

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        device: str | None = None,
        **kwargs,
    ) -> Self:
        from dolphin import load_model

        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")
        self.dolphin = load_model(
            model_name="small", model_dir=str(checkpoint_dir), device=device, **kwargs
        )
        return self

    def get_config(self):
        raise NotImplementedError

    def load(self, save_dir, **kwargs):
        raise NotImplementedError

    def save(self, save_dir, **kwargs):
        raise NotImplementedError
