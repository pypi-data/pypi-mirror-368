from typing import Tuple, Union, List
import numpy as np
import torch
import math
from torch import Tensor


def fast_fbank_lfr_cmvn(
    waveform: np.ndarray,
    cmvn: np.ndarray,
    lfr_m: int = 5,
    lfr_n: int = 1,
    n_mels: int = 80,
    window: str = "hamming",
    frame_length: int = 25,
    frame_shift: int = 10,
    dither: float = 0.0,
    **kwargs,
) -> Tuple[np.ndarray, np.ndarray]:
    waveform = torch.from_numpy(waveform)

    feats = fast_fbank(waveform, n_mels, window, frame_length, frame_shift, dither)

    feats = feats.numpy().astype(np.float32)
    feats_len = np.array(feats.shape[0]).astype(np.int32)

    # LFR
    LFR_inputs = []
    inputs = feats
    T = inputs.shape[0]
    T_lfr = int(np.ceil(T / lfr_n))
    left_padding = np.tile(inputs[0], ((lfr_m - 1) // 2, 1))
    inputs = np.vstack((left_padding, inputs))
    T = T + (lfr_m - 1) // 2
    for i in range(T_lfr):
        if lfr_m <= T - i * lfr_n:
            LFR_inputs.append((inputs[i * lfr_n : i * lfr_n + lfr_m]).reshape(1, -1))
        else:
            # process last LFR frame
            num_padding = lfr_m - (T - i * lfr_n)
            frame = inputs[i * lfr_n :].reshape(-1)
            for _ in range(num_padding):
                frame = np.hstack((frame, inputs[-1]))

            LFR_inputs.append(frame)
    LFR_outputs = np.vstack(LFR_inputs).astype(np.float32)

    # CMVN
    inputs = LFR_outputs
    frame, dim = inputs.shape
    means = np.tile(cmvn[0:1, :dim], (frame, 1))
    vars = np.tile(cmvn[1:2, :dim], (frame, 1))
    inputs = (inputs + means) * vars

    feats = inputs
    feats_len = np.array(feats.shape[0]).astype(np.int32)
    return feats, feats_len


def load_cmvn(
    file_path: str = "checkpoints/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch/am.mvn",
    return_numpy: bool = False,
):
    with open(file_path, "r", encoding="utf-8") as f:
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

    if return_numpy:
        means = np.array(means_list).astype(np.float64)
        vars = np.array(vars_list).astype(np.float64)
        cmvn = np.array([means, vars])
        return cmvn
    else:
        means = torch.tensor(means_list).float()
        vars = torch.tensor(vars_list).float()
        cmvn = torch.stack([means, vars])
        return cmvn


def fast_fbank(
    waveform: torch.Tensor,
    n_mels: int = 80,
    frame_length: int = 25,
    frame_shift: int = 10,
    dither: float = 0.0,
    sample_rate: int = 16000,
    remove_dc_offset: bool = True,
    raw_energy: bool = True,
    energy_floor: float = 0.0,
    preemphasis_coefficient: float = 0.97,
    use_power: bool = True,
    low_freq: float = 20.0,
    high_freq: float = 0.0,
    vtln_low: float = 100.0,
    vtln_high: float = -500.0,
    vtln_warp: float = 1.0,
    use_log_fbank: bool = True,
    round_to_power_of_two: bool = True,
) -> torch.Tensor:
    """基于 torchaudio和torch compile的快速fbank特征提取，输入为torch.Tensor类型的音频波形。
    fbank： 分帧 -》 高斯噪声 -》 移除直流分量 -》 计算能量 -》 预加重 -》 加窗 -》 傅里叶变换 -》 mel滤波器 -》 取对数

    Args:
        waveform (torch.Tensor): 输入的音频波形，shape为[T]，T为音频长度
        n_mels (int, optional): mel滤波器个数. Defaults to 80.
        frame_length (int, optional): 帧长,单位ms. Defaults to 25.
        frame_shift (int, optional): 帧移，单位ms. Defaults to 10.
        dither (float, optional): dither参数. Defaults to 0.0.
        sample_rate (int, optional): 采样率. Defaults to 16000.
        remove_dc_offset (bool, optional): 是否移除直流分量. Defaults to True.
        raw_energy (bool, optional): 是否计算原始能量,如果是则在预加重之前计算能量. Defaults to True.
        energy_floor (float, optional): 能量的最小值. Defaults to 0.0.
        preemphasis_coefficient (float, optional): 预加重系数. Defaults to 0.97.
        use_power (bool, optional): 是否使用功率谱. Defaults to True.
        low_freq (float, optional): 最低频率. Defaults to 20.0.
        high_freq (float, optional): 最高频率. Defaults to 0.0.
        vtln_low (float, optional): vtln warp的低频. Defaults to 100.0.
        vtln_high (float, optional): vtln warp的高频. Defaults to -500.0.
        vtln_warp (float, optional): vtln warp的系数. Defaults to 1.0.
        use_log_fbank (bool, optional): 是否对fbank结果取对数. Defaults to True.
        round_to_power_of_two (bool, optional): 是否将帧长调整为2的幂次方. Defaults to True.

    Returns:
        torch.Tensor: fbank特征，shape为[T, n_mels]
    """
    dtype, device = waveform.dtype, waveform.device
    waveform = waveform * (1 << 15)
    num_samples = waveform.size(0)
    eps = torch.tensor(torch.finfo(torch.float).eps)

    # 分帧
    window_length = int(frame_length * 16000 / 1000)
    window_shift = int(frame_shift * 16000 / 1000)
    m = 1 + (num_samples - window_length) // window_shift
    size = (m, window_length)
    strides = (window_shift, 1)
    strided_input = waveform.as_strided(size, strides)

    if dither > 0:
        # 高斯噪声
        rand_gauss = torch.randn(strided_input.shape, device=device, dtype=dtype)
        strided_input = strided_input + dither * rand_gauss

    if remove_dc_offset:
        # 移除直流分量
        # strided_input -= strided_input.mean(dim=1, dtype=dtype).unsqueeze(1)
        row_means = torch.mean(strided_input, dim=1).unsqueeze(1)  # size (m, 1)
        strided_input = strided_input - row_means
        strided_input = strided_input.to(device=device, dtype=dtype)

    if raw_energy:
        # 计算原始能量
        signal_log_energy = torch.max(strided_input.pow(2).sum(dim=-1), eps).log()
        if energy_floor > 0:
            signal_log_energy = torch.max(
                signal_log_energy,
                torch.tensor(math.log(energy_floor), device=device, dtype=dtype),
            )

    # 预加重
    if preemphasis_coefficient != 0:
        # strided_input[i,j] -= preemphasis_coefficient * strided_input[i, max(0, j-1)] for all i,j
        offset_strided_input = torch.nn.functional.pad(
            strided_input.unsqueeze(0), (1, 0), mode="replicate"
        ).squeeze(0)  # size (m, window_size + 1)
        strided_input = (
            strided_input - preemphasis_coefficient * offset_strided_input[:, :-1]
        )

    # 加窗
    window_function = torch.hamming_window(
        window_length, periodic=False, alpha=0.54, beta=0.46, device=device, dtype=dtype
    ).unsqueeze(0)

    strided_input = strided_input * window_function

    if round_to_power_of_two:
        # 将帧长调整为2的幂次方
        padded_window_length = _next_power_of_2(window_length)
        if padded_window_length != window_length:
            padding_right = padded_window_length - window_length
            strided_input = torch.nn.functional.pad(
                strided_input.unsqueeze(0), (0, padding_right), mode="constant", value=0
            ).squeeze(0)

    if not raw_energy:
        # 计算能量
        signal_log_energy = torch.max(strided_input.pow(2).sum(1), eps).log()
        if energy_floor > 0:
            signal_log_energy = torch.max(
                signal_log_energy,
                torch.tensor(math.log(energy_floor), device=device, dtype=dtype),
            )

    # 傅里叶变换
    # size (m, padded_window_size // 2 + 1)
    spectrum = torch.fft.rfft(strided_input).abs()

    # 功率谱
    if use_power:
        spectrum = spectrum.pow(2.0)

    # mel滤波器
    mel_energies, _ = get_mel_banks(
        n_mels,
        padded_window_length,
        sample_rate,
        low_freq,
        high_freq,
        vtln_low,
        vtln_high,
        vtln_warp,
    )
    mel_energies = mel_energies.to(device=device, dtype=dtype)
    # pad right column with zeros and add dimension, size (num_mel_bins, padded_window_size // 2 + 1)
    mel_energies = torch.nn.functional.pad(
        mel_energies, (0, 1), mode="constant", value=0
    )
    # sum with mel fiterbanks over the power spectrum, size (m, num_mel_bins)
    mel_energies = torch.mm(spectrum, mel_energies.T)

    # 取对数
    if use_log_fbank:
        # avoid log of zero (which should be prevented anyway by dithering)
        mel_energies = torch.max(mel_energies, eps).log()

    return mel_energies


def get_mel_banks(
    num_bins: int,
    window_length_padded: int,
    sample_freq: float,
    low_freq: float,
    high_freq: float,
    vtln_low: float,
    vtln_high: float,
    vtln_warp_factor: float,
) -> Tuple[Tensor, Tensor]:
    """
    Returns:
        (Tensor, Tensor): The tuple consists of ``bins`` (which is
        melbank of size (``num_bins``, ``num_fft_bins``)) and ``center_freqs`` (which is
        center frequencies of bins of size (``num_bins``)).
    """
    assert num_bins > 3, "Must have at least 3 mel bins"
    assert window_length_padded % 2 == 0
    num_fft_bins = window_length_padded / 2
    nyquist = 0.5 * sample_freq

    if high_freq <= 0.0:
        high_freq += nyquist

    assert (
        (0.0 <= low_freq < nyquist)
        and (0.0 < high_freq <= nyquist)
        and (low_freq < high_freq)
    ), "Bad values in options: low-freq {} and high-freq {} vs. nyquist {}".format(
        low_freq, high_freq, nyquist
    )

    # fft-bin width [think of it as Nyquist-freq / half-window-length]
    fft_bin_width = sample_freq / window_length_padded
    mel_low_freq = mel_scale_scalar(low_freq)
    mel_high_freq = mel_scale_scalar(high_freq)

    # divide by num_bins+1 in next line because of end-effects where the bins
    # spread out to the sides.
    mel_freq_delta = (mel_high_freq - mel_low_freq) / (num_bins + 1)

    if vtln_high < 0.0:
        vtln_high += nyquist

    assert vtln_warp_factor == 1.0 or (
        (low_freq < vtln_low < high_freq)
        and (0.0 < vtln_high < high_freq)
        and (vtln_low < vtln_high)
    ), (
        "Bad values in options: vtln-low {} and vtln-high {}, versus "
        "low-freq {} and high-freq {}".format(vtln_low, vtln_high, low_freq, high_freq)
    )

    bin = torch.arange(num_bins).unsqueeze(1)
    left_mel = mel_low_freq + bin * mel_freq_delta  # size(num_bins, 1)
    center_mel = mel_low_freq + (bin + 1.0) * mel_freq_delta  # size(num_bins, 1)
    right_mel = mel_low_freq + (bin + 2.0) * mel_freq_delta  # size(num_bins, 1)

    if vtln_warp_factor != 1.0:
        left_mel = vtln_warp_mel_freq(
            vtln_low, vtln_high, low_freq, high_freq, vtln_warp_factor, left_mel
        )
        center_mel = vtln_warp_mel_freq(
            vtln_low, vtln_high, low_freq, high_freq, vtln_warp_factor, center_mel
        )
        right_mel = vtln_warp_mel_freq(
            vtln_low, vtln_high, low_freq, high_freq, vtln_warp_factor, right_mel
        )

    center_freqs = inverse_mel_scale(center_mel)  # size (num_bins)
    # size(1, num_fft_bins)
    mel = mel_scale(fft_bin_width * torch.arange(num_fft_bins)).unsqueeze(0)

    # size (num_bins, num_fft_bins)
    up_slope = (mel - left_mel) / (center_mel - left_mel)
    down_slope = (right_mel - mel) / (right_mel - center_mel)

    if vtln_warp_factor == 1.0:
        # left_mel < center_mel < right_mel so we can min the two slopes and clamp negative values
        bins = torch.max(torch.zeros(1), torch.min(up_slope, down_slope))
    else:
        # warping can move the order of left_mel, center_mel, right_mel anywhere
        bins = torch.zeros_like(up_slope)
        up_idx = torch.gt(mel, left_mel) & torch.le(
            mel, center_mel
        )  # left_mel < mel <= center_mel
        down_idx = torch.gt(mel, center_mel) & torch.lt(
            mel, right_mel
        )  # center_mel < mel < right_mel
        bins[up_idx] = up_slope[up_idx]
        bins[down_idx] = down_slope[down_idx]

    return bins, center_freqs


def mel_scale_scalar(freq: float) -> float:
    return 1127.0 * math.log(1.0 + freq / 700.0)


def mel_scale(freq: Tensor) -> Tensor:
    return 1127.0 * (1.0 + freq / 700.0).log()


def inverse_mel_scale_scalar(mel_freq: float) -> float:
    return 700.0 * (math.exp(mel_freq / 1127.0) - 1.0)


def inverse_mel_scale(mel_freq: Tensor) -> Tensor:
    return 700.0 * ((mel_freq / 1127.0).exp() - 1.0)


def vtln_warp_freq(
    vtln_low_cutoff: float,
    vtln_high_cutoff: float,
    low_freq: float,
    high_freq: float,
    vtln_warp_factor: float,
    freq: Tensor,
) -> Tensor:
    r"""This computes a VTLN warping function that is not the same as HTK's one,
    but has similar inputs (this function has the advantage of never producing
    empty bins).

    This function computes a warp function F(freq), defined between low_freq
    and high_freq inclusive, with the following properties:
        F(low_freq) == low_freq
        F(high_freq) == high_freq
    The function is continuous and piecewise linear with two inflection
        points.
    The lower inflection point (measured in terms of the unwarped
        frequency) is at frequency l, determined as described below.
    The higher inflection point is at a frequency h, determined as
        described below.
    If l <= f <= h, then F(f) = f/vtln_warp_factor.
    If the higher inflection point (measured in terms of the unwarped
        frequency) is at h, then max(h, F(h)) == vtln_high_cutoff.
        Since (by the last point) F(h) == h/vtln_warp_factor, then
        max(h, h/vtln_warp_factor) == vtln_high_cutoff, so
        h = vtln_high_cutoff / max(1, 1/vtln_warp_factor).
          = vtln_high_cutoff * min(1, vtln_warp_factor).
    If the lower inflection point (measured in terms of the unwarped
        frequency) is at l, then min(l, F(l)) == vtln_low_cutoff
        This implies that l = vtln_low_cutoff / min(1, 1/vtln_warp_factor)
                            = vtln_low_cutoff * max(1, vtln_warp_factor)
    Args:
        vtln_low_cutoff (float): Lower frequency cutoffs for VTLN
        vtln_high_cutoff (float): Upper frequency cutoffs for VTLN
        low_freq (float): Lower frequency cutoffs in mel computation
        high_freq (float): Upper frequency cutoffs in mel computation
        vtln_warp_factor (float): Vtln warp factor
        freq (Tensor): given frequency in Hz

    Returns:
        Tensor: Freq after vtln warp
    """
    assert vtln_low_cutoff > low_freq, (
        "be sure to set the vtln_low option higher than low_freq"
    )
    assert vtln_high_cutoff < high_freq, (
        "be sure to set the vtln_high option lower than high_freq [or negative]"
    )
    l = vtln_low_cutoff * max(1.0, vtln_warp_factor)  # noqa
    h = vtln_high_cutoff * min(1.0, vtln_warp_factor)
    scale = 1.0 / vtln_warp_factor
    Fl = scale * l  # F(l)
    Fh = scale * h  # F(h)
    assert l > low_freq and h < high_freq
    # slope of left part of the 3-piece linear function
    scale_left = (Fl - low_freq) / (l - low_freq)
    # [slope of center part is just "scale"]

    # slope of right part of the 3-piece linear function
    scale_right = (high_freq - Fh) / (high_freq - h)

    res = torch.empty_like(freq)

    outside_low_high_freq = torch.lt(freq, low_freq) | torch.gt(
        freq, high_freq
    )  # freq < low_freq || freq > high_freq
    before_l = torch.lt(freq, l)  # freq < l
    before_h = torch.lt(freq, h)  # freq < h
    after_h = torch.ge(freq, h)  # freq >= h

    # order of operations matter here (since there is overlapping frequency regions)
    res[after_h] = high_freq + scale_right * (freq[after_h] - high_freq)
    res[before_h] = scale * freq[before_h]
    res[before_l] = low_freq + scale_left * (freq[before_l] - low_freq)
    res[outside_low_high_freq] = freq[outside_low_high_freq]

    return res


def vtln_warp_mel_freq(
    vtln_low_cutoff: float,
    vtln_high_cutoff: float,
    low_freq,
    high_freq: float,
    vtln_warp_factor: float,
    mel_freq: Tensor,
) -> Tensor:
    r"""
    Args:
        vtln_low_cutoff (float): Lower frequency cutoffs for VTLN
        vtln_high_cutoff (float): Upper frequency cutoffs for VTLN
        low_freq (float): Lower frequency cutoffs in mel computation
        high_freq (float): Upper frequency cutoffs in mel computation
        vtln_warp_factor (float): Vtln warp factor
        mel_freq (Tensor): Given frequency in Mel

    Returns:
        Tensor: ``mel_freq`` after vtln warp
    """
    return mel_scale(
        vtln_warp_freq(
            vtln_low_cutoff,
            vtln_high_cutoff,
            low_freq,
            high_freq,
            vtln_warp_factor,
            inverse_mel_scale(mel_freq),
        )
    )


def _next_power_of_2(x: int) -> int:
    r"""Returns the smallest power of 2 that is greater than x"""
    return 1 if x == 0 else 2 ** (x - 1).bit_length()


@torch.compile
def fast_pad_feats(feats: List[np.array], max_feat_len: Union[int, np.array]):
    padded_feats = []
    for feat in feats:
        if feat.shape[0] == max_feat_len:
            padded_feats.append(feat)
        else:
            pad_width = ((0, max_feat_len - feat.shape[0]), (0, 0))
            padded_feat = np.pad(feat, pad_width, "constant", constant_values=0)
            padded_feats.append(padded_feat)
    return np.array(padded_feats).astype(np.float32)
