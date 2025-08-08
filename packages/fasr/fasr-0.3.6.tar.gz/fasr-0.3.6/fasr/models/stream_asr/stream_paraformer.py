from typing import Dict, Iterable
from typing_extensions import Self
from pathlib import Path

from funasr import AutoModel
from funasr_onnx.paraformer_online_bin import Paraformer as ParaformerONNX
import torch
import numpy as np
from loguru import logger

from fasr.config import registry
from fasr.data import AudioToken, AudioChunk
from .base import StreamASRModel


@registry.stream_asr_models.register("stream_paraformer.torch")
class ParaformerForStreamASR(StreamASRModel):
    """Paraformer流式语音识别模型"""

    checkpoint: str = (
        "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online"
    )
    endpoint: str = "modelscope"

    chunk_size_ms: int = 600  # chunk size in ms
    encoder_chunk_look_back: int = (
        4  # number of chunks to lookback for encoder self-attention
    )
    decoder_chunk_look_back: int = 1
    sample_rate: int = 16000

    paraformer: AutoModel | None = None

    def transcribe_chunk(self, chunk: AudioChunk) -> Iterable[AudioToken]:
        if chunk.is_start and chunk.stream_id in self.states:
            logger.warning(
                "found start chunk with existing state, this is not expected"
            )
            del self.states[chunk.stream_id]
        state: Dict = self.states.get(chunk.stream_id, {})
        waveform = chunk.waveform
        if waveform.sample_rate != self.sample_rate:
            waveform = waveform.resample(self.sample_rate)
        sample_rate = waveform.sample_rate
        data = waveform.data
        chunk_size = int(self.chunk_size_ms * sample_rate / 1000)
        buffer = state.get("buffer", np.array([], dtype=np.float32))
        buffer = np.concatenate([buffer, data], axis=0)
        cache = state.get("cache", {})
        if chunk.is_last:
            stream = self.paraformer.generate(
                input=buffer,
                cache=cache,
                is_final=True,
                chunk_size=[0, 10, 5],
                encoder_chunk_look_back=self.encoder_chunk_look_back,
                decoder_chunk_look_back=self.decoder_chunk_look_back,
            )
            for result in stream:
                if result["text"]:
                    yield AudioToken(text=result["text"])
        else:
            while len(buffer) > chunk_size:
                input_data = buffer[:chunk_size]
                buffer = buffer[chunk_size:]
                stream = self.paraformer.generate(
                    input=input_data,
                    cache=cache,
                    is_final=False,
                    chunk_size=[0, 10, 5],  # chunk size 10 * 60ms
                    encoder_chunk_look_back=self.encoder_chunk_look_back,
                    decoder_chunk_look_back=self.decoder_chunk_look_back,
                )
                for result in stream:
                    if result["text"]:
                        yield AudioToken(text=result["text"])
        state["buffer"] = buffer
        state["cache"] = cache
        self.states[chunk.stream_id] = state
        if chunk.is_last:
            self.states.pop(chunk.stream_id)

    def reset(self):
        self.states.clear()

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        disable_update: bool = True,
        disable_log: bool = True,
        disable_pbar: bool = True,
        compile: bool = False,
        **kwargs,
    ) -> Self:
        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")
        self.paraformer = AutoModel(
            model=checkpoint_dir,
            disable_update=disable_update,
            disable_log=disable_log,
            disable_pbar=disable_pbar,
            **kwargs,
        )
        if compile:
            logger.info("using torch.compile for stream paraformer")
            self.paraformer.model = torch.compile(
                self.paraformer.model, fullgraph=True, dynamic=True
            )
        return self


@registry.stream_asr_models.register("stream_paraformer.onnx")
class ParaformerForStreamASROnnx(StreamASRModel):
    """Paraformer流式语音识别模型"""

    checkpoint: str = (
        "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online"
    )
    endpoint: str = "modelscope"
    chunk_size_ms: int = 600  # chunk size in ms
    encoder_chunk_look_back: int = (
        4  # number of chunks to lookback for encoder self-attention
    )
    decoder_chunk_look_back: int = 1
    sample_rate: int = 16000
    paraformer: ParaformerONNX = None

    def transcribe_chunk(self, chunk: AudioChunk) -> Iterable[AudioToken]:
        if chunk.is_start and chunk.stream_id in self.states:
            logger.warning(
                "found start chunk with existing state, this is not expected"
            )
            del self.states[chunk.stream_id]
        state = self.states.get(chunk.stream_id, {})
        waveform = chunk.waveform
        if waveform.sample_rate != self.sample_rate:
            waveform = waveform.resample(self.sample_rate)
        sample_rate = waveform.sample_rate
        data = waveform.data
        chunk_size = int(self.chunk_size_ms * sample_rate / 1000)
        buffer = state.get("buffer", np.array([], dtype=np.float32))
        buffer = np.concatenate([buffer, data], axis=0)
        cache = state.get("cache", {})
        param_dict = {"cache": cache}
        if chunk.is_last:
            param_dict["is_final"] = True
            stream = self.paraformer(
                audio_in=buffer,
                param_dict=param_dict,
            )
            for result in stream:
                if result["preds"]:
                    for t in result["preds"][1]:
                        yield AudioToken(text=t)
        else:
            while len(buffer) > chunk_size:
                audio_in = buffer[:chunk_size]
                buffer = buffer[chunk_size:]
                stream = self.paraformer(
                    audio_in=audio_in,
                    param_dict=param_dict,
                )
                for result in stream:
                    if result["preds"]:
                        for t in result["preds"][1]:
                            yield AudioToken(text=t)
        state["buffer"] = buffer
        state["cache"] = cache
        self.states[chunk.stream_id] = state
        if chunk.is_last:
            self.states.pop(chunk.stream_id)

    def from_checkpoint(
        self,
        checkpoint_dir: str | Path | None = None,
        quantize: bool = False,
        device: str | None = None,
        intra_op_num_threads: int = 4,
        **kwargs,
    ) -> Self:
        if not checkpoint_dir:
            checkpoint_dir = self.download_checkpoint()
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")
        if not device:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            device_id = 0
        else:
            device_id = -1
        self.paraformer = ParaformerONNX(
            model_dir=checkpoint_dir,
            chunk_size=[0, 10, 5],
            quantize=quantize,
            device_id=device_id,
            intra_op_num_threads=intra_op_num_threads,
            **kwargs,
        )
        return self
