import numpy as np
from fasr.utils import read_yaml
from fasr.config import registry, Config
from fasr.data import Waveform
from pathlib import Path
from torchaudio.compliance.kaldi import fbank as torchaudio_fbank
import torch
from pydantic import model_validator, Field
from .base import BaseWaveformPreprocessor
from torch import Tensor


@registry.waveform_preprocessors.register("fbank_extractor")
class FbankExtractor(BaseWaveformPreprocessor):
    """Conventional frontend structure for ASR."""

    fs: int = 16000
    window: str = "hamming"
    n_mels: int = 80
    frame_length: int = 25
    frame_shift: int = 10
    lfr_m: int = 5
    lfr_n: int = 1
    dither: float = 0.0
    round_to_power_of_two: bool = True
    snip_edges: bool = True
    cmvn_tensor: Tensor | np.ndarray | None = Field(
        None, description="CMVN tensor", title="CMVN tensor"
    )
    compile: bool = False

    @model_validator(mode="after")
    def compile_fbank(self):
        if self.compile:
            import torch._dynamo.config

            torch._dynamo.config.suppress_errors = True
            torch._dynamo.config.numpy_default_float = "float32"
            global torchaudio_fbank
            torchaudio_fbank = torch.compile(torchaudio_fbank)
            data = np.random.randn(1000)
            waveform = Waveform(data=data, sample_rate=self.fs)
            _ = self.process_waveform(waveform=waveform)
        return self

    def process_waveform(self, waveform: Waveform, device: str = "cpu") -> Waveform:
        if waveform.sample_rate != self.fs:
            waveform = waveform.resample(self.fs)
        data = waveform.data
        with torch.device(device):
            feats = self.apply_fbank(data)
        if self.lfr_m != 1 or self.lfr_n != 1:
            feats = self.apply_lfr(feats)
        if self.cmvn_tensor is not None:
            feats = self.apply_cmvn(feats)
        waveform.feats = feats
        return waveform

    def apply_fbank(self, waveform: np.ndarray) -> np.ndarray:
        waveform = waveform * (1 << 15)
        waveform = torch.from_numpy(waveform)
        feat = torchaudio_fbank(
            waveform.unsqueeze(0),
            channel=0,
            num_mel_bins=self.n_mels,
            window_type=self.window,
            frame_length=self.frame_length,
            frame_shift=self.frame_shift,
            round_to_power_of_two=self.round_to_power_of_two,
            dither=self.dither,
            sample_frequency=self.fs,
            energy_floor=0,
            snip_edges=self.snip_edges,
        )
        return feat.cpu().numpy().astype(np.float32)

    def apply_lfr(self, inputs: np.ndarray) -> np.ndarray:
        """低帧率技术"""
        LFR_inputs = []
        lfr_m, lfr_n = self.lfr_m, self.lfr_n
        T = inputs.shape[0]
        T_lfr = int(np.ceil(T / lfr_n))
        left_padding = np.tile(inputs[0], ((lfr_m - 1) // 2, 1))
        inputs = np.vstack((left_padding, inputs))
        T = T + (lfr_m - 1) // 2
        for i in range(T_lfr):
            if lfr_m <= T - i * lfr_n:
                LFR_inputs.append(
                    (inputs[i * lfr_n : i * lfr_n + lfr_m]).reshape(1, -1)
                )
            else:
                # process last LFR frame
                num_padding = lfr_m - (T - i * lfr_n)
                frame = inputs[i * lfr_n :].reshape(-1)
                for _ in range(num_padding):
                    frame = np.hstack((frame, inputs[-1]))

                LFR_inputs.append(frame)
        LFR_outputs = np.vstack(LFR_inputs).astype(np.float32)
        return LFR_outputs

    def apply_cmvn(self, inputs: np.ndarray) -> np.ndarray:
        """
        Apply CMVN with mvn data
        """
        frame, dim = inputs.shape
        means = np.tile(self.cmvn_tensor[0:1, :dim], (frame, 1))
        vars = np.tile(self.cmvn_tensor[1:2, :dim], (frame, 1))
        inputs = (inputs + means) * vars
        return inputs

    def warmup(self) -> None:
        waveform = np.random.randn(10000).astype(np.float32)
        self.process_waveform(waveform)

    def from_checkpoint(self, checkpoint_dir: str, **kwargs) -> "FbankExtractor":
        config: dict = read_yaml(Path(checkpoint_dir, "config.yaml"))["frontend_conf"]
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        cmvn_file = str(Path(checkpoint_dir, "am.mvn"))
        cmvn_tensor = load_cmvn_tensor(cmvn_file)
        self.cmvn_tensor = cmvn_tensor
        return self

    def get_config(self) -> Config:
        data = {
            "audio_preprocessor": {
                "@audio_preprocessors": "fbank_extractor",
                "fs": self.fs,
                "window": self.window,
                "n_mels": self.n_mels,
                "frame_length": self.frame_length,
                "frame_shift": self.frame_shift,
                "lfr_m": self.lfr_m,
                "lfr_n": self.lfr_n,
                "dither": self.dither,
                "round_to_power_of_two": self.round_to_power_of_two,
                "compile": self.compile,
            }
        }
        return Config(data=data)

    def save(self, save_dir: str) -> None:
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        config_path = save_dir / "config.cfg"
        cmvn_path = save_dir / "cmvn.npy"
        np.save(cmvn_path, self.cmvn_tensor)
        self.get_config().to_disk(config_path)

    def load(self, save_dir: str) -> "FbankExtractor":
        save_dir = Path(save_dir)
        cmvn_path = save_dir / "cmvn.npy"
        self.cmvn_tensor = np.load(cmvn_path)
        return self


def low_frame_rate(inputs: Tensor, lfr_m: Tensor, lfr_n: Tensor) -> Tensor:
    LFR_inputs = []
    T = inputs.shape[0]
    T_lfr = int(np.ceil(T / lfr_n))
    left_padding = inputs[0].repeat((lfr_m - 1) // 2, 1)
    inputs = torch.vstack((left_padding, inputs))
    T = T + (lfr_m - 1) // 2
    for i in range(T_lfr):
        if lfr_m <= T - i * lfr_n:
            LFR_inputs.append((inputs[i * lfr_n : i * lfr_n + lfr_m]).view(1, -1))
        else:  # process last LFR frame
            num_padding = lfr_m - (T - i * lfr_n)
            frame = (inputs[i * lfr_n :]).view(-1)
            for _ in range(num_padding):
                frame = torch.hstack((frame, inputs[-1]))
            LFR_inputs.append(frame)
    LFR_outputs = torch.vstack(LFR_inputs)
    return LFR_outputs.type(torch.float32)


def load_cmvn_tensor(
    cmvn_file: str,
) -> Tensor:
    with open(cmvn_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    means_list = []
    vars_list = []
    for i in range(len(lines)):
        line_item = lines[i].split()
        if line_item[0] == "<AddShift>":
            line_item = lines[i + 1].split()
            if line_item[0] == "<LearnRateCoef>":
                add_shift_line = line_item[3 : (len(line_item) - 1)]
                means_list = list(add_shift_line)
                continue
        elif line_item[0] == "<Rescale>":
            line_item = lines[i + 1].split()
            if line_item[0] == "<LearnRateCoef>":
                rescale_line = line_item[3 : (len(line_item) - 1)]
                vars_list = list(rescale_line)
                continue

    means = np.array(means_list).astype(np.float64)
    vars = np.array(vars_list).astype(np.float64)
    cmvn = np.array([means, vars]).astype(np.float32)
    return cmvn
