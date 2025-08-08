from .base import ASRModel
from typing_extensions import Self
from typing import List
from funasr import AutoModel
from fasr.config import registry
from fasr.data import AudioToken, AudioTokenList
from pathlib import Path
import numpy as np
import torch
import re


@registry.asr_models.register("sensevoice")
class SensevoiceForASR(ASRModel):
    checkpoint: str = "iic/SenseVoiceSmall"
    endpoint: str = "modelscope"

    sensevoice: AutoModel | None = None

    def transcribe(
        self, batch: List[np.ndarray | torch.Tensor], **kwargs
    ) -> List[List[AudioToken]]:
        fs = kwargs.get("sample_rate", 16000)
        use_itn = kwargs.get("use_itn", False)
        results = self.sensevoice.generate(input=batch, fs=fs, use_itn=use_itn)
        batch_tokens = []
        for result in results:
            tokens = AudioTokenList()
            pattern = r"<\|(.+?)\|><\|(.+?)\|><\|(.+?)\|><\|(.+?)\|>(.+)"
            if result["text"]:
                match = re.match(pattern, result["text"])
                if match:
                    language, emotion, audio_type, itn, text = match.groups()
                    for s in text.strip():
                        if s != " ":
                            tokens.append(AudioToken(text=s))
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
        self.sensevoice = model
        return self

    def get_config(self):
        raise NotImplementedError

    def load(self, save_dir, **kwargs):
        raise NotImplementedError

    def save(self, save_dir, **kwargs):
        raise NotImplementedError
