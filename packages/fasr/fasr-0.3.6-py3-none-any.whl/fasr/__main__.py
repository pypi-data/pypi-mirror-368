from typing import Literal
from pathlib import Path

from jsonargparse import auto_cli

from fasr.utils.base import download, FASR_DEFAULT_CACHE_DIR


class Prepare:
    """准备类"""

    def __init__(self):
        pass

    def offline(self, cache_dir: str | Path = FASR_DEFAULT_CACHE_DIR):
        """离线模型准备"""

        models = [
            "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
            "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        ]
        for model in models:
            download(model_id=model, cache_dir=cache_dir)

    def online(self, cache_dir: str | Path = FASR_DEFAULT_CACHE_DIR):
        """在线模型准备"""
        models = [
            "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online",
            "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
            "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        ]
        for model in models:
            download(repo_id=model, cache_dir=cache_dir)


class Benchmark:
    """基准测试类"""

    def __init__(self):
        pass

    def loader(
        self,
        urls: str,
        loader: Literal["loader.v1", "loader.v2"] = "loader.v2",
        num_threads: int = 4,
    ):
        """测试fasr的loader性能.

        Args:
            loader (Literal["loader.v1", "loader.v2"]): loader.v1使用多线程, loader.v2使用异步加载.
            urls (str): url文件路径, 每行一个url.
            num_threads (int, optional): 并行处理的工作线程数，仅对loader.v1有效. Defaults to 4.
        """
        import time
        from loguru import logger
        from fasr.config import registry

        if loader == "loader.v1":
            loader = registry.components.get(loader)(num_threads=num_threads)
        else:
            loader = registry.components.get(loader)()

        if not Path(urls).exists():
            raise FileNotFoundError(f"{urls} not found")
        if Path(urls).is_dir():
            urls = [
                str(p)
                for p in Path(urls).iterdir()
                if p.is_file() and p.suffix == ".wav"
            ]
        else:
            with open(urls, "r") as f:
                urls = f.readlines()
            urls = [url.strip() for url in urls]

        # warm up
        _ = urls[:5] | loader

        # benchmark
        start = time.perf_counter()
        audios = urls | loader
        end = time.perf_counter()
        took = round(end - start, 2)
        duration = audios.duration_s
        logger.info(f"took {took} seconds, speedup: {round(duration / took, 2)}")

    def vad(
        self,
        urls: str,
        model: str = "fsmn",
        batch_size: int = 2,
        num_threads: int = 2,
        num_samples: int | None = None,
        audio_format: Literal["wav", "mp3"] = "wav",
    ):
        """对比测试fasr与funasr pipeline(load -> vad)的性能.

        Args:
            urls (str): url文件路径, 每行一个url.
            batch_size (int, optional): 批处理大小. Defaults to 2.
            num_threads (int, optional): 并行处理的工作线程数. Defaults to 2.
            num_samples (int, optional): 采样数量. Defaults to 100.
            model_dir (str, optional): 语音检测模型目录. Defaults to "checkpoints/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch".
        """
        import time
        from tqdm import trange
        from loguru import logger
        from fasr.data import Audio, AudioList
        from fasr.components import VoiceDetector

        vad = VoiceDetector().setup(model=model, num_threads=num_threads)

        if not Path(urls).exists():
            raise FileNotFoundError(f"{urls} not found")
        if Path(urls).is_dir():
            urls = [
                str(p)
                for p in Path(urls).iterdir()
                if p.is_file() and p.suffix == f".{audio_format}"
            ]
        else:
            with open(urls, "r") as f:
                urls = f.readlines()
            urls = [url.strip() for url in urls]
        if num_samples:
            urls = urls[:num_samples]

        audios = AudioList[Audio]()
        duration = 0
        for idx in range(0, len(urls), batch_size):
            batch_urls = urls[idx : idx + batch_size]
            batch_audios = AudioList.from_urls(
                urls=batch_urls, load=True, num_workers=4
            )
            for audio in batch_audios:
                duration += audio.duration * len(audio.channels)
            audios.extend(batch_audios)

        def run_vad(audios: AudioList[Audio]) -> float:
            start = time.perf_counter()
            for i in trange(0, len(audios), batch_size):
                _audios = audios[i : i + batch_size]
                _audios = vad.predict(_audios)
            end = time.perf_counter()
            took = round(end - start, 2)
            return took

        # warm up
        logger.info("warm up")
        _ = run_vad(audios[0:1])

        # benchmark
        fasr_took = run_vad(audios)
        logger.info(f"All channels duration: {round(duration, 2)} seconds")
        logger.info(
            f"{model}: took {fasr_took} seconds, speedup: {round(duration / fasr_took, 2)}"
        )

    def stream_vad(
        self,
        model: Literal["stream_fsmn.torch", "stream_fsmn.onnx"] = "stream_fsmn.torch",
        max_silence: int = 500,
        threshold: float = 0.8,
        chunk_size_ms: int = 200,
        db_threshold: int = -100,
        print_infer_time: bool = False,
        interactive: bool = False,
    ):
        """流式语音活动检测"""
        import time
        from fasr.models.stream_vad import StreamVADModel
        from fasr.data import AudioChunk, AudioBytesStream, Audio, AudioSpan
        from fasr.config import registry
        from loguru import logger

        vad: StreamVADModel = registry.stream_vad_models.get(model)(
            chunk_size_ms=chunk_size_ms,
            max_end_silence_time=max_silence,
            speech_noise_thres=threshold,
            db_threshold=db_threshold,
        ).from_checkpoint()

        if interactive:
            import pyaudio

            FORMAT = pyaudio.paInt16
            RATE = 16000
            chunk_size_ms = chunk_size_ms
            CHUNK = int(RATE / 1000 * chunk_size_ms)

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )
            bytes_buffer = AudioBytesStream(
                sample_rate=RATE, chunk_size_ms=chunk_size_ms
            )
            logger.info("开始录音...")
            while True:
                bytes_data = stream.read(CHUNK)
                chunks = bytes_buffer.push(bytes_data)
                for chunk in chunks:
                    chunk: AudioChunk
                    if print_infer_time:
                        start = time.perf_counter()
                    for span in vad.detect_chunk(chunk=chunk):
                        logger.info(f"speech {span.vad_state}")
                    if print_infer_time:
                        end = time.perf_counter()
                        spend = round(end - start, 4)
                        duration = chunk.duration_s
                        speedup = round(duration / spend, 4)
                        rtf = round(spend / duration, 4)
                        logger.info(
                            f"chunk duration: {duration}, spend: {spend}, speedup: {speedup}, rtf: {rtf}"
                        )
        else:
            audio = Audio().load_example(example="asr")
            chunks = audio.chunk(chunk_size_ms=chunk_size_ms)
            spent_times = []
            for chunk in chunks:
                chunk: AudioChunk
                start = time.perf_counter()
                for span in vad.detect_chunk(chunk):
                    end = time.perf_counter()
                    spend = end - start
                    span: AudioSpan
                    if span.vad_state == "start":
                        logger.info(f"speech start: {span.start_ms}")
                    elif span.vad_state == "end":
                        logger.info(f"speech end: {span.end_ms}")
                    spent_times.append(spend)
            mean_spend = round(sum(spent_times) / len(spent_times), 5)
            speedup = round(chunk_size_ms / mean_spend / 1000, 4)
            rtf = round(mean_spend / (chunk_size_ms / 1000), 4)
            logger.info(
                f"chunk size: {chunk_size_ms} ms, mean spend: {mean_spend} s, speedup: {speedup}, rtf: {rtf}"
            )

    def asr(
        self,
        urls: str,
        model: str = "paraformer",
        batch_size: int = 2,
        num_threads: int = 1,
        num_samples: int | None = None,
    ):
        """测试asr推理性能.

        Args:
            urls (str): url文件路径.
            batch_size (int, optional): 批处理大小. Defaults to 2.
            num_threads (int, optional): 并行处理的工作线程数. Defaults to 2.
            num_samples (int, optional): 采样数量. Defaults to 100.
            model_dir (str, optional): 语音检测模型目录. Defaults to "checkpoints/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch".
        """
        import time
        from loguru import logger
        from tqdm import trange
        from fasr.data import Audio, AudioList
        from fasr.components import SpeechRecognizer, AudioLoaderV2

        asr = SpeechRecognizer().setup(model=model, num_threads=num_threads)
        loader = AudioLoaderV2()

        if not Path(urls).exists():
            raise FileNotFoundError(f"{urls} not found")
        if Path(urls).is_dir():
            urls = [
                str(p)
                for p in Path(urls).iterdir()
                if p.is_file() and p.suffix == ".wav"
            ]
        else:
            with open(urls, "r") as f:
                urls = f.readlines()
            urls = [url.strip() for url in urls]
        if num_samples:
            urls = urls[:num_samples]

        audios = AudioList[Audio]()
        duration = 0
        for idx in range(0, len(urls), batch_size):
            batch_urls = urls[idx : idx + batch_size]
            batch_audios = AudioList.from_urls(urls=batch_urls)
            batch_audios = loader.predict(batch_audios)
            for audio in batch_audios:
                duration += audio.duration * len(audio.channels)
            audios.extend(batch_audios)

        def run_asr(audios: AudioList[Audio]) -> float:
            start = time.perf_counter()
            for i in trange(0, len(audios), batch_size):
                _audios = audios[i : i + batch_size]
                _audios = asr.predict(_audios)
            end = time.perf_counter()
            took = round(end - start, 2)
            return took

        # warm up
        logger.info("warm up")
        _ = run_asr(audios[0:1])

        # benchmark
        fasr_took = run_asr(audios)
        logger.info(f"All channels duration: {round(duration, 2)} seconds")
        logger.info(
            f"{model}: took {fasr_took} seconds, speedup: {round(duration / fasr_took, 2)}"
        )

    def stream_asr(
        self,
        model: Literal[
            "stream_paraformer.torch", "stream_paraformer.onnx", "stream_sensevoice"
        ] = "stream_paraformer.onnx",
        checkpoint_dir: str | Path | None = None,
        chunk_size_ms: int = 600,
        interactive: bool = False,
        compile: bool = False,
        device: str = None,
    ):
        """流式语音识别"""
        import time
        from loguru import logger
        from fasr.config import registry
        from fasr.models.stream_asr.base import StreamASRModel
        from fasr.data import Audio, AudioChunk, AudioBytesStream

        asr: StreamASRModel = registry.stream_asr_models.get(model)(
            chunk_size_ms=chunk_size_ms
        ).from_checkpoint(checkpoint_dir=checkpoint_dir, compile=compile, device=device)
        audio = Audio().load_example(example="asr")
        chunks = audio.chunk(chunk_size_ms=chunk_size_ms)
        if compile:
            logger.info("warm up model")
            for chunk in chunks:
                chunk: AudioChunk
                for token in asr.transcribe_chunk(chunk=chunk):
                    pass
        if interactive:
            import pyaudio

            FORMAT = pyaudio.paInt16
            RATE = 16000
            chunk_size_ms = chunk_size_ms
            CHUNK = int(RATE / 1000 * chunk_size_ms)
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )
            bytes_buffer = AudioBytesStream(
                sample_rate=RATE, chunk_size_ms=chunk_size_ms
            )
            logger.info("开始录音...")
            while True:
                bytes_data = stream.read(CHUNK)
                chunks = bytes_buffer.push(bytes_data)
                start = time.perf_counter()
                text = ""
                for chunk in chunks:
                    chunk: AudioChunk
                    for token in asr.transcribe_chunk(chunk=chunk):
                        text += token.text
                if text:
                    logger.info(text)
                    end = time.perf_counter()
                    spend = round(end - start, 4)
                    duration = chunk_size_ms / 1000
                    speedup = round(duration / spend, 4)
                    rtf = round(spend / duration, 4)
                    logger.info(
                        f"chunk size: {chunk_size_ms}ms, spend: {spend}, speedup: {speedup}, rtf: {rtf}"
                    )

        else:
            chunk_spends = []
            for chunk in chunks:
                start = time.perf_counter()
                chunk: AudioChunk
                text = ""
                for token in asr.transcribe_chunk(chunk=chunk):
                    text += token.text
                if text:
                    logger.info(text)
                    end = time.perf_counter()
                    chunk_spends.append(end - start)
            mean_spend = round(sum(chunk_spends) / len(chunk_spends), 5)
            speedup = round(chunk_size_ms / mean_spend / 1000, 4)
            rtf = round(mean_spend / (chunk_size_ms / 1000), 4)
            logger.info(
                f"chunk size: {chunk_size_ms} ms, mean spend: {mean_spend} s, speedup: {speedup}, rtf: {rtf}"
            )

    def pipeline(
        self,
        input: str,
        batch_size: int = 2,
        num_threads: int = 2,
        batch_size_s: int = 100,
        num_samples: int | None = None,
        asr_model: str = "paraformer",
        vad_model: str = "fsmn",
        punc_model: str = "ct_transformer",
        compile: bool = False,
    ):
        """对比测试fasr与funasr pipeline(load -> vad -> asr -> punc)的性能.

        Args:
            input (str): 测试文件，格式可以为一行为一个url的txt文件可以为AudioList保存格式.
            batch_size (int, optional): 批处理大小. Defaults to 2.
            batch_size_s (int, optional): asr模型的批处理大小. Defaults to 100.
            num_threads (int, optional): 并行处理的工作线程数. Defaults to 2.
            num_samples (int, optional): 采样数量. Defaults to 100.
            asr_model (str, optional): asr模型. Defaults to "paraformer".
            vad_model (str, optional): vad模型. Defaults to "fsmn".
            punc_model (str, optional): 标点模型. Defaults to "ct_transformer".
        """
        import time
        from loguru import logger
        from fasr.pipelines import AudioPipeline
        from fasr.data import AudioList

        def check_input_and_load(input: str) -> AudioList:
            """检查输入文件是否存在.

            Args:
                input (str): 输入文件路径.
            """
            if not Path(input).exists():
                raise FileNotFoundError(f"{input} not found")
            if Path(input).is_dir():
                files = [
                    str(p)
                    for p in Path(input).iterdir()
                    if p.is_file() and p.suffix == ".wav"
                ]
                audios = AudioList.from_urls(files)
            else:
                if Path(input).suffix == ".al":
                    audios = AudioList.load_binary(input)
                elif Path(input).suffix == ".txt":
                    with open(input, "r") as f:
                        urls = f.readlines()
                        urls = [url.strip() for url in urls]
                        audios = AudioList.from_urls(urls)
            return audios

        audios = check_input_and_load(input)
        audios = audios.load(num_workers=4)
        duration = audios.duration_s
        if num_samples:
            audios = audios[:num_samples]
        asr = (
            AudioPipeline()
            .add_pipe(
                "detector",
                num_threads=num_threads,
                compile=compile,
                model=vad_model,
                batch_size=batch_size,
            )
            .add_pipe(
                "recognizer",
                model=asr_model,
                batch_size_s=batch_size_s,
                batch_size=batch_size,
            )
            .add_pipe("sentencizer", model=punc_model, batch_size=batch_size)
        )

        def run_pipeline(urls):
            start = time.perf_counter()
            _ = asr.run(urls, verbose=True)
            end = time.perf_counter()
            took = round(end - start, 2)
            return took

        # warm up
        logger.info("warm up")
        _ = run_pipeline(audios[0:2])

        # benchmark
        logger.info("benchmark")
        pipeline_took = run_pipeline(audios)
        # 所有通道的总时长
        logger.info(f"duration: {round(duration, 2)} seconds")
        logger.info(
            f"pipeline: took {pipeline_took} seconds, speedup: {round(duration / pipeline_took, 2)}"
        )


class Serve:
    """服务类"""

    def __init__(self):
        pass

    def online(
        self,
        host: str = "0.0.0.0",
        port: int = 27000,
        device: str | None = None,
        vad_model: Literal[
            "stream_fsmn.torch", "stream_fsmn.onnx"
        ] = "stream_fsmn.torch",
        vad_chunk_size_ms: int = 100,
        vad_end_silence_ms: int = 500,
        vad_threshold: float = 0.6,
        vad_db_threshold: int = -100,
        asr_model: Literal[
            "stream_sensevoice", "stream_paraformer.onnx", "stream_paraformer.torch"
        ] = "stream_paraformer.torch",
        asr_checkpoint_dir: str | None = None,
        punc_model: Literal["ct_transformer"] | None = None,
        punc_checkpoint_dir: str | None = None,
        compile: bool = False,
    ):
        """流式语音识别"""
        from fasr.service.online import RealtimeASRService

        service = RealtimeASRService(
            host=host,
            port=port,
            device=device,
            asr_model_name=asr_model,
            asr_checkpoint_dir=asr_checkpoint_dir,
            vad_model_name=vad_model,
            vad_chunk_size_ms=vad_chunk_size_ms,
            vad_end_silence_ms=vad_end_silence_ms,
            vad_threshold=vad_threshold,
            vad_db_threshold=vad_db_threshold,
            punc_model_name=punc_model,
            punc_checkpoint_dir=punc_checkpoint_dir,
        )
        service.setup()

    def offline(self):
        """离线语音识别"""
        pass


commands = {
    "prepare": Prepare,
    "download": download,
    "benchmark": Benchmark,
    "serve": Serve,
}


def run():
    """命令行"""
    auto_cli(components=commands)


if __name__ == "__main__":
    run()
