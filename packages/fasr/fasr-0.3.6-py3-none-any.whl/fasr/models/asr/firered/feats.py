import kaldi_native_fbank as knf
import numpy as np
from numpy.typing import NDArray
from typing import List
import torch
import os
import kaldiio
import math


class KaldiFbankExtractor:
    def __init__(
        self,
        kaldi_cmvn_file: str = None,
        num_mel_bins: int = 80,
        frame_length: int = 25,
        frame_shift: int = 10,
        dither: float = 0.0,
    ):
        self.num_mel_bins = num_mel_bins
        self.frame_length = frame_length
        self.frame_shift = frame_shift
        self.dither = dither

        opts = knf.FbankOptions()
        opts.frame_opts.dither = dither
        opts.mel_opts.num_bins = num_mel_bins
        opts.frame_opts.snip_edges = True
        opts.mel_opts.debug_mel = False
        self.opts = opts

        self.cmvn = None
        if kaldi_cmvn_file is not None:
            self.cmvn = CMVN(kaldi_cmvn_file=kaldi_cmvn_file)

    def __call__(self, batch_data: List[NDArray], sample_rate: int) -> NDArray:
        feats = []
        for data in batch_data:
            data = data * (1 << 15)
            feat = self.fbank(data, sample_rate)
            if self.cmvn is not None:
                feat = self.cmvn(feat)
            feat = torch.from_numpy(feat).float()
            feats.append(feat)
        lengths = torch.tensor([feat.shape[0] for feat in feats]).long()
        feats = self.pad_feat(feats, 0)
        return feats, lengths

    def fbank(self, data: NDArray, sample_rate: int) -> NDArray:
        fbank = knf.OnlineFbank(self.opts)
        data = data.tolist()
        fbank.accept_waveform(sample_rate, data)
        feats = []
        for i in range(fbank.num_frames_ready):
            feats.append(fbank.get_frame(i))
        feats = np.vstack(feats)
        return feats

    def pad_feat(self, xs, pad_value):
        n_batch = len(xs)
        max_len = max([xs[i].size(0) for i in range(n_batch)])
        pad = (
            torch.ones(n_batch, max_len, *xs[0].size()[1:])
            .to(xs[0].device)
            .to(xs[0].dtype)
            .fill_(pad_value)
        )
        for i in range(n_batch):
            pad[i, : xs[i].size(0)] = xs[i]
        return pad


class CMVN:
    def __init__(self, kaldi_cmvn_file):
        self.dim, self.means, self.inverse_std_variences = self.read_kaldi_cmvn(
            kaldi_cmvn_file
        )

    def __call__(self, x, is_train=False):
        assert x.shape[-1] == self.dim, "CMVN dim mismatch"
        out = x - self.means
        out = out * self.inverse_std_variences
        return out

    def read_kaldi_cmvn(self, kaldi_cmvn_file):
        assert os.path.exists(kaldi_cmvn_file)
        stats = kaldiio.load_mat(kaldi_cmvn_file)
        assert stats.shape[0] == 2
        dim = stats.shape[-1] - 1
        count = stats[0, dim]
        assert count >= 1
        floor = 1e-20
        means = []
        inverse_std_variences = []
        for d in range(dim):
            mean = stats[0, d] / count
            means.append(mean.item())
            varience = (stats[1, d] / count) - mean * mean
            if varience < floor:
                varience = floor
            istd = 1.0 / math.sqrt(varience)
            inverse_std_variences.append(istd)
        return dim, np.array(means), np.array(inverse_std_variences)
