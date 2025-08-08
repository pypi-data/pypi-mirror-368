from fasr.data.audio import Audio, AudioList, AudioChannel, AudioChannelList
from fasr.data.waveform import Waveform
from fasr.config import registry, Config
from .base import BaseComponent
from pydantic import Field
from typing import List
from aiohttp import ClientSession
import asyncio
from io import BytesIO
import librosa
from pathlib import Path
import aiofiles
from joblib import Parallel, delayed
from pydub import AudioSegment
from loguru import logger
import numpy as np
import requests


LIBROSA_AVAILABLE_FORMATS = ["wav", "mp3"]


@registry.components.register("loader")
@registry.components.register("loader.v2")
class AudioLoaderV2(BaseComponent):
    """异步音频下载器，负责所有音频的并行下载和下载条件"""

    name: str = "loader"
    input_tags: List[str] = ["audio.url"]
    output_tags: List[str] = [
        "audio.waveform",
        "audio.duration",
        "audio.channels",
    ]

    max_duration_seconds: float | None = Field(
        None, alias="max_duration", description="音频最大时长，超过该时长则截断"
    )
    min_duration_seconds: float | None = Field(
        None, alias="min_duration", description="音频最小时长，小于该时长则不下载"
    )
    reload: bool = Field(False, description="是否重新下载")
    only_num_channels: int | None = Field(
        None, description="只下载指定通道数的音频，None表示不限制"
    )
    mono: bool | None = Field(None, description="是否合并多通道音频为单通道")

    def predict(self, audios: AudioList) -> AudioList:
        _ = asyncio.run(self.aload_audios(audios=audios))
        return audios

    async def aload_audio(self, audio: Audio, session: ClientSession) -> Audio:
        if not self.reload and audio.is_loaded:
            return audio
        mono = self.mono if audio.mono is None else audio.mono
        audio_format = get_audio_format(audio.url)
        try:
            if Path(audio.url).exists():
                try:
                    async with aiofiles.open(audio.url, "rb") as f:
                        bytes = await f.read()
                        bytes = BytesIO(bytes)
                        if audio_format not in LIBROSA_AVAILABLE_FORMATS:
                            bytes = convert_bytes(
                                bytes, target_format="wav", ori_format=audio_format
                            )
                        try:
                            data, sample_rate = librosa.load(
                                bytes, sr=audio.sample_rate, mono=mono
                            )
                        except Exception:
                            logger.warning(
                                f"librosa can't load audio, using pydub to convert audio format, url: {audio.url}"
                            )
                            bytes = convert_bytes(bytes, "wav", ori_format=None)
                            data, sample_rate = librosa.load(
                                bytes, sr=audio.sample_rate, mono=mono
                            )
                        duration = librosa.get_duration(y=data, sr=sample_rate)
                        audio.duration = round(duration, 4)
                        audio = assign_audio_data(audio, data, sample_rate)
                        audio = check_audio_duration(
                            audio, self.max_duration_seconds, self.min_duration_seconds
                        )
                        audio = check_audio_channels(audio, self.only_num_channels)
                except Exception as e:
                    audio.is_bad = True
                    audio.bad_reason = str(e)
                    audio.bad_component = self.name

                return audio

            async with session.get(audio.url) as response:
                if response.status == 200:
                    bytes = await response.read()
                    bytes = BytesIO(bytes)
                    if audio_format not in LIBROSA_AVAILABLE_FORMATS:
                        bytes = convert_bytes(
                            bytes, target_format="wav", ori_format=audio_format
                        )
                    try:
                        data, sample_rate = librosa.load(
                            bytes, sr=audio.sample_rate, mono=mono
                        )
                    except Exception:
                        logger.warning(
                            f"librosa can't load audio, using pydub to convert audio format, url: {audio.url}"
                        )
                        bytes = await response.read()
                        bytes = BytesIO(bytes)
                        bytes = convert_bytes(bytes, "wav", ori_format=None)
                        data, sample_rate = librosa.load(
                            bytes, sr=audio.sample_rate, mono=mono
                        )
                    duration = librosa.get_duration(y=data, sr=sample_rate)
                    audio.duration = round(duration, 4)
                    audio = assign_audio_data(audio, data, sample_rate)
                    audio = check_audio_duration(
                        audio, self.max_duration_seconds, self.min_duration_seconds
                    )
                    audio = check_audio_channels(audio, self.only_num_channels)
                else:
                    audio.is_bad = True
                    audio.bad_reason = f"下载音频失败，状态码{response.status}"
                    audio.bad_component = self.name

                return audio
        except Exception as e:
            audio.is_bad = True
            audio.bad_reason = str(e)
            audio.bad_component = self.name
            return audio

    async def aload_audios(self, audios: AudioList) -> AudioList:
        async with ClientSession() as session:
            tasks = [self.aload_audio(audio, session) for audio in audios]
            results = await asyncio.gather(*tasks)
            return results

    def get_config(self) -> Config:
        data = {
            "component": {
                "@components": "loader.v2",
                "max_duration": self.max_duration_seconds,
                "min_duration": self.min_duration_seconds,
                "reload": self.reload,
                "mono": self.mono,
                "only_num_channels": self.only_num_channels,
            }
        }
        return Config(data=data)

    def save(self, save_dir: str | Path) -> None:
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        config_path = save_dir / "config.cfg"
        self.get_config().to_disk(config_path)

    def load(self, save_dir: str | Path) -> "AudioLoaderV2":
        config_path = Path(save_dir, "config.cfg")
        config = Config().from_disk(config_path)
        loader = registry.resolve(config)["component"]
        return loader

    def setup(self, checkpoint_dir, device="cpu", compile=False, **kwargs):
        pass


@registry.components.register("loader.v1")
class AudioLoaderV1(BaseComponent):
    """多线程音频下载器，负责所有音频的并行下载和下载条件"""

    name: str = "loader"
    input_tags: List[str] = ["audio.url"]
    output_tags: List[str] = [
        "audio.waveform",
        "audio.sample_rate",
        "audio.duration",
        "audio.channels",
    ]

    max_duration_seconds: float | None = Field(
        None, alias="max_duration", description="音频最大时长，超过该时长则截断"
    )
    min_duration_seconds: float | None = Field(
        None, alias="min_duration", description="音频最小时长，小于该时长则不下载"
    )
    mono: bool | None = Field(None, description="是否合并多通道音频为单通道")
    reload: bool = Field(False, description="是否重新下载")
    num_threads: int = Field(1, description="最大并行线程数")
    only_num_channels: int | None = Field(
        None, description="只下载指定通道数的音频，None表示不限制"
    )

    def predict(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        _ = Parallel(
            n_jobs=self.num_threads,
            prefer="threads",
            pre_dispatch="10 * n_jobs",
        )(delayed(self.load_audio)(audio) for audio in audios)
        return audios

    def load_audio(self, audio: Audio) -> Audio:
        if not self.reload and audio.is_loaded:
            return audio
        mono = self.mono if audio.mono is None else audio.mono
        audio_format = get_audio_format(audio.url)
        try:
            if Path(audio.url).exists():
                try:
                    bytes = Path(audio.url).read_bytes()
                    bytes = BytesIO(bytes)
                    if audio_format not in LIBROSA_AVAILABLE_FORMATS:
                        bytes = convert_bytes(
                            bytes, target_format="wav", ori_format=audio_format
                        )
                    try:
                        data, sample_rate = librosa.load(
                            bytes, sr=audio.sample_rate, mono=mono
                        )
                    except Exception:
                        logger.warning(
                            f"librosa can't load audio, using pydub to convert audio format, url: {audio.url}"
                        )
                        bytes = Path(audio.url).read_bytes()
                        bytes = BytesIO(bytes)
                        bytes = convert_bytes(bytes, "wav", ori_format=None)
                        data, sample_rate = librosa.load(
                            bytes, sr=audio.sample_rate, mono=mono
                        )
                    duration = librosa.get_duration(y=data, sr=sample_rate)
                    audio.duration = round(duration, 2)
                    audio = assign_audio_data(audio, data, sample_rate)
                    audio = check_audio_duration(
                        audio, self.max_duration_seconds, self.min_duration_seconds
                    )
                    audio = check_audio_channels(audio, self.only_num_channels)
                except Exception as e:
                    audio.is_bad = True
                    audio.bad_reason = str(e)
                    audio.bad_component = self.name

                return audio

            bytes = requests.get(audio.url).content
            bytes = BytesIO(bytes)
            if audio_format not in LIBROSA_AVAILABLE_FORMATS:
                bytes = convert_bytes(
                    bytes, target_format="wav", ori_format=audio_format
                )
            try:
                data, sample_rate = librosa.load(bytes, sr=audio.sample_rate, mono=mono)
            except Exception:
                logger.warning(
                    f"librosa can't load audio, using pydub to convert audio format, url: {audio.url}"
                )
                bytes = requests.get(audio.url).content
                bytes = BytesIO(bytes)
                bytes = convert_bytes(bytes, "wav", ori_format=None)
                data, sample_rate = librosa.load(bytes, sr=audio.sample_rate, mono=mono)
            duration = librosa.get_duration(y=data, sr=sample_rate)
            audio.duration = round(duration, 2)
            audio = assign_audio_data(audio, data, sample_rate)
            audio = check_audio_duration(
                audio, self.max_duration_seconds, self.min_duration_seconds
            )
            audio = check_audio_channels(audio, self.only_num_channels)
        except Exception as e:
            audio.is_bad = True
            audio.bad_reason = str(e)
            audio.bad_component = self.name
        return audio

    def save(self, save_dir: str | Path) -> None:
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        config_path = save_dir / "config.cfg"
        self.get_config().to_disk(config_path)

    def load(self, save_dir: str | Path) -> "AudioLoaderV1":
        config_path = Path(save_dir, "config.cfg")
        config = Config().from_disk(config_path)
        loader = registry.resolve(config)["component"]
        return loader

    def get_config(self) -> Config:
        data = {
            "component": {
                "@components": "loader.v1",
                "max_duration": self.max_duration_seconds,
                "min_duration": self.min_duration_seconds,
                "reload": self.reload,
                "mono": self.mono,
                "num_threads": self.num_threads,
                "only_num_channels": self.only_num_channels,
            }
        }
        return Config(data=data)

    def setup(self, **kwargs):
        pass


def convert_bytes(
    bytes: BytesIO, target_format: str, ori_format: str | None = None
) -> BytesIO:
    """using pydub to convert bytes to another format bytes.

    Args:
        bytes (BytesIO): The bytes to be converted.
        target_format (str): The target format.
        ori_format (str | None, optional): The original format. Defaults to None.

    Returns:
        BytesIO: The converted bytes.
    """
    segment: AudioSegment = AudioSegment.from_file(bytes, format=ori_format)
    bytes = BytesIO()
    segment.export(bytes, format=target_format)
    return bytes


def get_audio_format(url: str) -> str | None:
    """Get audio format from url.

    Args:
        url (str): The url of audio.

    Returns:
        str: The format of audio.
    """
    formats = [".mp3", ".wav", ".amr", ".m4a", ".flac", ".aac", ".ogg"]
    for format in formats:
        if format in url:
            return format.replace(".", "")
    return None


def assign_audio_data(audio: Audio, data: np.ndarray, sample_rate: int) -> Audio:
    """Assign audio data to audio.

    Args:
        audio (Audio): The audio to be assigned.
        data (np.ndarray): The audio data.
        sample_rate (int): The sample rate of audio.

    Returns:
        Audio: The audio with data assigned.
    """
    if len(data.shape) == 1:
        audio.mono = True
        audio.channels = AudioChannelList[AudioChannel](
            [
                AudioChannel(
                    id=audio.id,
                    waveform=Waveform(data=data, sample_rate=sample_rate),
                )
            ]
        )
    else:
        audio.mono = False
        audio.channels = AudioChannelList[AudioChannel](
            [
                AudioChannel(
                    id=audio.id,
                    waveform=Waveform(data=channel_data, sample_rate=sample_rate),
                )
                for channel_data in data
            ]
        )
    return audio


def check_audio_duration(
    audio: Audio,
    max_duration_seconds: float | None = None,
    min_duration_seconds: float | None = None,
) -> Audio:
    """Check audio duration.

    Args:
        audio (Audio): The audio to be checked.
        max_duration (float | None): The max duration of audio.
        min_duration (float | None): The min duration of audio.

    Returns:
        Audio: The audio with duration checked.
    """
    if max_duration_seconds and audio.duration > max_duration_seconds:
        audio.is_bad = True
        audio.bad_reason = f"音频时长超过最大时长限制{max_duration_seconds}s, 当前时长{audio.duration}s"
    if min_duration_seconds and audio.duration < min_duration_seconds:
        audio.is_bad = True
        audio.bad_reason = f"音频时长小于最小时长限制{min_duration_seconds}s, 当前时长{audio.duration}s"

    if audio.is_bad:
        audio.bad_component = "loader"
    return audio


def check_audio_channels(audio: Audio, only_num_channels: int | None = None) -> Audio:
    """Check audio channels.

    Args:
        audio (Audio): The audio to be checked.
        only_num_channels (int | None): The number of channels.

    Returns:
        Audio: The audio with channels checked.
    """
    if only_num_channels and len(audio.channels) != only_num_channels:
        audio.is_bad = True
        audio.bad_reason = f"音频通道数不符合要求, 期望{only_num_channels}通道，实际{len(audio.channels)}通道"
    if audio.is_bad:
        audio.bad_component = "loader"
    return audio
