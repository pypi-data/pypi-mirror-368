from asyncio import Queue, Event
from pathlib import Path
import asyncio
import traceback
from urllib.parse import parse_qs
from typing import Literal, List

from loguru import logger
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, Field, ConfigDict

from fasr.config import registry
from fasr.data import AudioBytesStream, AudioChunk, AudioToken, AudioChunkList
from fasr.models.stream_asr.base import StreamASRModel
from fasr.models.stream_vad.base import StreamVADModel
from fasr.models.asr.base import ASRModel
from fasr.models.punc.base import PuncModel
from .schema import AudioChunkResponse, TranscriptionResponse


class RealtimeASRService(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, extra="ignore"
    )
    # service
    host: str = Field("127.0.0.1", description="服务地址")
    port: int = Field(27000, description="服务端口")
    device: Literal["cpu", "cuda", "mps"] | None = Field(None, description="设备")

    # audio input
    sample_rate: int = Field(16000, description="音频采样率")
    bit_depth: int = Field(16, description="音频位深")
    channels: int = Field(1, description="音频通道数")

    # speech
    min_speech_duration_ms: int = Field(500, description="最小语音持续时间, 单位ms")

    # 1pass model
    asr_model_name: Literal[
        "stream_sensevoice", "stream_paraformer.torch", "stream_paraformer.onnx"
    ] = Field("stream_paraformer.torch", description="流式asr模型")
    asr_checkpoint_dir: str | Path | None = Field(
        None,
        description="asr模型路径",
    )
    asr_model: StreamASRModel = Field(None, description="asr模型")

    vad_model_name: Literal["stream_fsmn.torch", "stream_fsmn.onnx"] = Field(
        "stream_fsmn.torch", description="流式vad模型"
    )
    vad_model: StreamVADModel = Field(None, description="vad模型")
    vad_checkpoint_dir: str | Path | None = Field(
        None,
    )
    vad_chunk_size_ms: int = Field(100, description="音频分片大小")
    vad_end_silence_ms: int = Field(500, description="vad判定音频片段结束最大静音时间")
    vad_threshold: float = Field(
        0.6,
        description="vad判定阈值, 取值范围0~1，值越大，则需要更大声音量来触发vad，噪音环境下建议设置更高的阈值",
        le=1,
        ge=0,
    )
    vad_db_threshold: int = Field(
        -100,
        description="vad音量阈值,值越大，则需要更大音量来触发vad，噪音环境下建议设置更高的阈值",
    )

    # 2pass model
    offline_asr_model_name: Literal["sensevoice", "paraformer"] = Field(
        None, description="离线asr模型"
    )
    offline_asr_checkpoint_dir: str | Path | None = Field(
        None,
        description="asr模型路径",
    )
    offline_asr_model: ASRModel = Field(None, description="离线asr模型")

    punc_model_name: Literal["ct_transformer"] = Field(None, description="标点模型")
    punc_model: PuncModel = Field(None, description="标点模型")
    punc_checkpoint_dir: str | Path | None = Field(
        None,
    )

    def setup(self):
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(
            f"Start online ASR Service on {self.host}:{self.port}, device: {self.device}"
        )
        logger.info(
            f"ASR Model: {self.asr_model_name}, VAD Model: {self.vad_model_name}, Punc Model: {self.punc_model_name or 'None'}, Offline ASR Model: {self.offline_asr_model_name or 'None'}"
        )
        logger.info(
            f"VAD Config: chunk_size_ms: {self.vad_chunk_size_ms}, end_silence_ms: {self.vad_end_silence_ms}, threshold: {self.vad_threshold}, db_threshold: {self.vad_db_threshold}"
        )

        self.asr_model: StreamASRModel = registry.stream_asr_models.get(
            self.asr_model_name
        )()
        self.asr_model.from_checkpoint(
            checkpoint_dir=self.asr_checkpoint_dir,
            device=self.device,
        )
        self.vad_model: StreamVADModel = registry.stream_vad_models.get(
            self.vad_model_name
        )(
            chunk_size_ms=self.vad_chunk_size_ms,
            max_end_silence_time=self.vad_end_silence_ms,
            speech_noise_thres=self.vad_threshold,
            db_threshold=self.vad_db_threshold,
        )
        self.vad_model.from_checkpoint(
            checkpoint_dir=self.vad_checkpoint_dir,
            device=self.device,
        )
        if self.offline_asr_model_name is not None:
            self.offline_asr_model: ASRModel = registry.asr_models.get(
                self.offline_asr_model_name
            )()
            self.offline_asr_model.from_checkpoint(
                checkpoint_dir=self.offline_asr_checkpoint_dir,
                device=self.device,
            )
        if self.punc_model_name is not None:
            self.punc_model: PuncModel = registry.punc_models.get(
                self.punc_model_name
            )()
            self.punc_model.from_checkpoint(
                checkpoint_dir=self.punc_checkpoint_dir,
                device=self.device,
            )

        @app.websocket("/asr/realtime")
        async def transcribe(ws: WebSocket):
            try:
                # 解析请求参数
                await ws.accept()
                query_params = parse_qs(ws.scope["query_string"].decode())
                itn = query_params.get("itn", ["false"])[0].lower() == "true"
                model = query_params.get("model", ["paraformer"])[0].lower()
                chunk_size = int(self.vad_chunk_size_ms * self.sample_rate / 1000)
                logger.info(f"itn: {itn}, chunk_size: {chunk_size}, model: {model}")
                span_queue = Queue()
                bytes_buffer = AudioBytesStream(
                    sample_rate=self.sample_rate, chunk_size_ms=self.vad_chunk_size_ms
                )
                vad_is_done = Event()
                tasks = []
                tasks.append(
                    asyncio.create_task(
                        self.vad_task(
                            ws,
                            span_queue=span_queue,
                            bytes_buffer=bytes_buffer,
                            vad_done_event=vad_is_done,
                        )
                    )
                )
                tasks.append(
                    asyncio.create_task(
                        self.asr_task(
                            ws=ws, span_queue=span_queue, vad_is_done=vad_is_done
                        )
                    )
                )
                _done, _ = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.error(
                    f"Unexpected error: {e}\nCall stack:\n{traceback.format_exc()}"
                )
                await ws.close()
            finally:
                self.vad_model.remove_state(bytes_buffer._id)
                self.asr_model.remove_state(bytes_buffer._id)
                logger.info("Cleaned up resources after WebSocket disconnect")

        uvicorn.run(app, host=self.host, port=self.port, ws="wsproto")

    async def vad_task(
        self,
        ws: WebSocket,
        span_queue: Queue,
        bytes_buffer: AudioBytesStream,
        vad_done_event: Event,
    ):
        logger.info("start vad task")
        while True:
            try:
                raw_data = await ws.receive()
            except Exception as e:
                logger.error(f"Error receiving data: {e}")
                vad_done_event.set()
                break
            bytes_data = raw_data.get("bytes", None)
            if bytes_data is None:
                logger.warning("Received data is None")
                continue
            chunks: List[AudioChunk] = bytes_buffer.push(bytes_data)
            for chunk in chunks:
                for segment_chunk in self.vad_model.detect_chunk(chunk=chunk):
                    segment_chunk: AudioChunk
                    if segment_chunk.vad_state != "segment_mid":
                        await self.send_vad_response(
                            "",
                            ws,
                            segment_chunk.vad_state,
                            start_time=segment_chunk.start_ms,
                            end_time=segment_chunk.end_ms,
                        )
                    await span_queue.put(segment_chunk)

    async def asr_task(self, ws: WebSocket, span_queue: Queue, vad_is_done: Event):
        final_text = ""
        segment: AudioChunkList = AudioChunkList()
        while not vad_is_done.is_set():
            span: AudioChunk = await span_queue.get()
            segment.append(span)
            is_last = span.vad_state == "segment_end"
            if is_last:
                if self.offline_asr_model is None:
                    for token in self.asr_model.transcribe_chunk(chunk=span):
                        final_text += token.text
                        await self.send_asr_response(
                            final_text, ws, "interim_transcript"
                        )
                    segment_chunk: AudioChunk = segment.concat_to_chunk()
                    if (
                        len(final_text) > 0
                        and segment_chunk.duration_ms >= self.min_segment_duration_ms
                    ):
                        if self.punc_model is not None:
                            restored_text = self.punc_model.restore(final_text).text
                            await self.send_asr_response(
                                restored_text,
                                ws,
                                "final_transcript",
                                start_time=segment_chunk.start_ms,
                                end_time=segment_chunk.end_ms,
                                raw_text=final_text,
                            )
                        else:
                            await self.send_asr_response(
                                final_text,
                                ws,
                                "final_transcript",
                                start_time=segment_chunk.start_ms,
                                end_time=segment_chunk.end_ms,
                            )
                else:
                    segment_chunk: AudioChunk = segment.concat_to_chunk()
                    segment_data = segment_chunk.waveform.data
                    final_text = self.offline_asr_model.transcribe(
                        batch=[segment_data]
                    )[0].text
                    if (
                        len(final_text) > 0
                        and segment_chunk.duration_ms >= self.min_segment_duration_ms
                    ):
                        if self.punc_model is not None:
                            restored_text = self.punc_model.restore(final_text).text
                        else:
                            restored_text = final_text
                        await self.send_asr_response(
                            restored_text,
                            ws,
                            "final_transcript",
                            start_time=segment_chunk.start_ms,
                            end_time=segment_chunk.end_ms,
                            raw_text=final_text,
                        )
                    self.asr_model.remove_state(
                        segment_chunk.stream_id
                    )  # clear state, because the segment is ended

                final_text = ""
                segment = AudioChunkList()
            else:
                for token in self.asr_model.transcribe_chunk(chunk=span):
                    token: AudioToken
                    final_text += token.text
                    await self.send_asr_response(final_text, ws, "interim_transcript")
            span_queue.task_done()

    async def send_asr_response(
        self,
        text: str,
        ws: WebSocket,
        state: str,
        start_time: float = None,
        end_time: float = None,
        raw_text: str = None,
    ):
        if raw_text is not None:
            if len(raw_text) == 1 and text in ["嗯", "啊"]:
                return
        if len(text) > 0:
            response = TranscriptionResponse(
                data=AudioChunkResponse(
                    text=text, state=state, start_time=start_time, end_time=end_time
                )
            )
            await ws.send_json(response.model_dump())
            logger.info(f"asr state: {state}, text: {text}")

    async def send_vad_response(
        self,
        text: str,
        ws: WebSocket,
        state: str,
        start_time: float = None,
        end_time: float = None,
    ):
        response = TranscriptionResponse(
            data=AudioChunkResponse(
                text=text, state=state, start_time=start_time, end_time=end_time
            )
        )
        await ws.send_json(response.model_dump())
        logger.info(f"vad state: {state}")

    @property
    def min_segment_duration_ms(self) -> int:
        return self.min_speech_duration_ms + self.vad_end_silence_ms
