from pydantic import validate_call, ConfigDict, Field, model_validator, BaseModel
from fasr.components.base import BaseComponent
from fasr.components import AudioLoaderV1
from fasr.data import Audio, AudioList
from fasr.config import registry, Config
from fasr.utils.base import IOMixin
from typing import List, Iterable, Literal
from typing_extensions import Self
from collections import OrderedDict
from loguru import logger
from queue import Queue, Empty
from pathlib import Path
import time
import threading


class AudioQueue(Queue):
    """Create a queue object with a given audio duration limit.

    item in the queue is a tuple of (Audio, Queue).
    """

    def _qsize(self) -> int | bool:
        if len(self.queue) == 0:
            return False  # line 139 Queue._get: while self._qsize() >= self.maxsize: this will be False
        durations = []
        for item in self.queue:
            audio, queue = item
            audio: Audio
            if audio.duration is not None:
                durations.append(audio.duration)
        qsize = round(sum(durations), 2)
        if qsize == 0:
            qsize = 1  # though the audio duration is 0, the queue is not empty, if the queue is empty, will raise Empty
        return qsize


def run_component(
    component: BaseComponent, audios: AudioList[Audio]
) -> AudioList[Audio]:
    """Run a component to process the audio data

    Args:
        component (BaseComponent): the component to process the audio data
        audios (AudioList[Audio]): the audio data to process

    Returns:
        AudioList[Audio]: the processed audio data
    """
    start = time.perf_counter()
    audios = audios | component
    end = time.perf_counter()
    spent = end - start
    for audio in audios:
        audio: Audio
        if audio.spent_time is None:
            audio.spent_time = {}
        if audio.spent_time.get(component.name) is None:
            audio.spent_time[component.name] = spent
        else:
            audio.spent_time[component.name] += spent
        audio.spent_time[component.name] = round(audio.spent_time[component.name], 3)
    return audios


class PipelineResult(BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    request_queue: AudioQueue | None = Field(None, description="the request queue")
    response_queue: Queue | None = Field(None, description="the response queue")
    loader: BaseComponent | None = Field(None, description="the loader component")

    num_inputs: int = Field(0, description="the number of inputs")
    num_outputs: int = Field(0, description="the number of outputs")

    @validate_call
    def add_task(self, input: str | List[str] | Audio | AudioList):
        """Add a task to the pipeline"""
        input = self.loader._to_audios(input)
        input = run_component(component=self.loader, audios=input)
        self.num_inputs += len(input)
        if isinstance(input, Audio):
            self.request_queue.put((input, self.response_queue))
        elif isinstance(input, AudioList):
            for audio in input:
                self.request_queue.put((audio, self.response_queue))

    def stream_result(self, timeout: float = 100) -> Iterable[Audio]:
        while self.num_outputs < self.num_inputs:
            try:
                audio: Audio = self.response_queue.get(timeout=timeout)
                yield audio
                self.response_queue.task_done()
                self.num_outputs += 1
            except Empty:
                break

    def get_next_result(self, timeout: float = 100) -> Audio | None:
        """Get the next result from the pipeline

        Args:
            timeout (float, optional): the timeout of the response queue waiting for one audio. Defaults to 100. in seconds.

        Returns:
            Audio: the processed audio data.
        """

        try:
            audio: Audio = self.response_queue.get(timeout=timeout)
            self.response_queue.task_done()
            self.num_outputs += 1
            return audio
        except Empty:
            return None


@registry.pipes.register("thread_pipe")
class Pipe(IOMixin):
    """Pipe is a component in the pipeline that can process the audio data in parallel"""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    component: BaseComponent | None = Field(
        None, description="the component to process the audio"
    )
    verbose: bool = Field(False, description="whether to print detailed logs")
    input_queue: AudioQueue | None = None
    output_queue: AudioQueue | None = None
    batch_timeout: float = Field(0.01, description="dynamic batch timeout", ge=0)
    batch_size: int | None = Field(1, description="dynamic batch size", ge=1)
    is_last: bool = Field(True, description="whether it is the last component")
    stop_event: threading.Event | None = Field(None, description="stop event")
    thread: threading.Thread | None = Field(default=None, description="thread object")

    @model_validator(mode="after")
    def validate_stop_event(self):
        if self.stop_event is None:
            self.stop_event = threading.Event()
        return self

    def predict(self, audios: AudioList[Audio]) -> AudioList[Audio]:
        """Predict the audio data"""
        audios = run_component(component=self.component, audios=audios)
        return audios

    def run_loop(self):
        while not self.stop_event.is_set():
            batch = self.dynamic_batch()
            if len(batch) == 0:
                continue
            audios = AudioList([audio for audio, response_queue in batch])
            start = time.perf_counter()
            _ = self.predict(audios)
            end = time.perf_counter()
            spent = round(end - start, 2)
            if self.verbose and spent > 0:
                logger.info(
                    f"{self.component.name} processed {audios.duration_s}s audios, remaining {float(self.input_queue.qsize())}s, speed {round(audios.duration_s / spent, 2)}x"
                )
            if self.is_last or self.output_queue is None:
                for audio, response_queue in batch:
                    response_queue: Queue
                    response_queue.put(audio)
            else:
                for item in batch:
                    self.output_queue.put(item)
                    self.input_queue.task_done()

    def dynamic_batch(self):
        entered_at = time.monotonic()
        end_time = entered_at + self.batch_timeout
        batch = []
        if self.batch_size is None:
            batch_size = 1e6
        else:
            batch_size = self.batch_size
        while time.monotonic() < end_time and len(batch) < batch_size:
            try:
                audio, response_queue = self.input_queue.get(timeout=self.batch_timeout)
                batch.append((audio, response_queue))
            except Exception:
                break
        return batch

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.daemon = True
        self.thread.name = self.component.name
        self.thread.start()

    def restart(self):
        """restart the thread"""
        # check if the thread is alive
        if self.thread.is_alive():
            self.stop_event.set()  # set the stop event
            self.thread.join()  # wait for the thread to stop
            # clear output queue
            if self.output_queue:
                while not self.output_queue.empty():
                    self.output_queue.get()
                    self.output_queue.task_done()
            if self.input_queue:
                while not self.input_queue.empty():
                    self.input_queue.get()
                    self.input_queue.task_done()
        self.start()

    def get_config(self) -> Config:
        data = {
            "pipe": {
                "@pipes": "thread_pipe",
                "batch_timeout": self.batch_timeout,
                "batch_size": self.batch_size,
            }
        }
        config = Config(data=data)
        return config

    def save(self, save_dir: str):
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
        config = self.get_config()
        config.to_disk(save_dir / "config.cfg")
        self.component.save(save_dir / "component")

    def load(self, save_dir: str):
        save_dir = Path(save_dir)
        config = Config().from_disk(save_dir / "config.cfg")
        pipe = registry.resolve(config)["pipe"]
        self.batch_size = pipe.batch_size
        self.batch_timeout = pipe.batch_timeout
        component_dir = save_dir / "component"
        component_config = Config().from_disk(component_dir / "config.cfg")
        component: BaseComponent = registry.resolve(component_config)["component"]
        self.component = component.load(component_dir)
        return self

    @property
    def name(self) -> str | None:
        if self.component is None:
            return None
        return self.component.name

    @property
    def input_tags(self) -> List[str]:
        if self.component is None:
            return []
        return self.component.input_tags

    @property
    def output_tags(self) -> List[str]:
        if self.component is None:
            return []
        return self.component.output_tags


@registry.pipelines.register("audio_pipeline")
class AudioPipeline(IOMixin):
    """Audio Pipeline start with a loader component which can load the audio data from the disk or other sources.
    Args:
        loader (BaseComponent | Literal["v1", "v2"], optional): the loader component. Defaults to AudioLoaderV1.
        pipes (OrderedDict[str, Pipe] | None, optional): the components in the pipeline. Defaults to None.
        request_queue (AudioQueue | None, optional): the request queue. Defaults to None.
    """

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    loader: BaseComponent | Literal["loader.v1", "loader.v2"] = Field(
        default_factory=AudioLoaderV1, description="the loader component"
    )
    pipes: OrderedDict[str, Pipe] | None = Field(
        default=None, description="the components in the pipeline"
    )
    request_queue: AudioQueue | None = Field(
        default=None, description="the request queue"
    )

    @model_validator(mode="after")
    def validate_pipes(self):
        if self.pipes is None:
            self.pipes = OrderedDict()
        if self.request_queue is None:
            self.request_queue = AudioQueue()
        if isinstance(self.loader, str):
            self.loader = registry.components.get(self.loader)(num_threads=2)
        return self

    @validate_call
    def __call__(
        self,
        input: str | Audio | Path,
        verbose: bool = False,
        clear: bool = False,
        timeout: float | None = None,
    ) -> Audio:
        return self.run(input, verbose=verbose, clear=clear, timeout=timeout)[0]

    @validate_call
    def run(
        self,
        input: str | Path | Audio | List[str] | AudioList | List[Path],
        timeout: float | None = None,
        verbose: bool = False,
        clear: bool = False,
    ) -> AudioList[Audio]:
        """Run the pipeline

        Args:
            input (str | Audio | List[str] | AudioList): the input data, can be a path, an Audio object, a list of paths or a list of Audio objects.
            timeout (float | None, optional): the timeout of the response queue. Defaults to None.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            clear (bool, optional): whether to clear the audio data after processing. Defaults to False.

        Returns:
            AudioList[Audio]: the processed audio data
        """
        for _, pipe in self.pipes.items():
            pipe.verbose = verbose
        response_queue = Queue()
        audios = self.loader._to_audios(input)
        for audio in audios:
            if audio.is_bad:
                response_queue.put(audio)
        results = AudioList[Audio]()
        start = time.perf_counter()
        for i in range(0, len(audios), 10):
            batch_audios = audios[i : i + 10]
            batch_audios = run_component(component=self.loader, audios=batch_audios)
            if len(self.pipe_names) > 0:
                for audio in batch_audios:
                    self.request_queue.put((audio, response_queue))
            else:
                results.extend(batch_audios)

        while True:
            if len(audios) == len(results):
                break
            try:
                audio: Audio = response_queue.get(timeout=timeout)
                if clear:
                    audio.clear()
                results.append(audio)
                response_queue.task_done()
            except Empty:
                logger.error("response queue timeout")
                for audio in audios:
                    if not audio.is_bad:
                        audio.is_bad = True
                        audio.bad_reason = "response queue timeout"
                break
            except KeyboardInterrupt:
                logger.error("KeyboardInterrupt, waiting for restart")
                self.restart()
                logger.info("Pipeline restart success")
                break
        end = time.perf_counter()
        spent = max(round(end - start, 2), 1e-5)
        if len(audios) == len(results):
            if not response_queue.empty():
                logger.error("response not equal to request")
                for audio in audios:
                    if not audio.is_bad:
                        audio.is_bad = True
                        audio.bad_reason = "response not equal to request"
            else:
                if verbose:
                    if (
                        not audios.has_bad_audio()
                        and spent > 0
                        and len(self.pipe_names) > 0
                    ):
                        logger.info(
                            f"pipeline processed {results.duration_s}s audios, spent {spent}s, speed {round(results.duration_s / spent, 2)}x"
                        )
        return audios

    @validate_call
    def stream(
        self,
        input: str | Audio | List[str] | AudioList,
        timeout: float | None = None,
        clear: bool = False,
        verbose: bool = False,
    ) -> Iterable[Audio]:
        """Stream the audio data. return the processed audio data one by one.
        Args:
            input (str | Audio | List[str] | AudioList): the input data, can be a path, an Audio object, a list of paths or a list of Audio objects.
            timeout (float | None, optional): the timeout of the response queue waiting for one audio. Defaults to None.
            clear (bool, optional): whether to clear the audio data after processing. Defaults to True.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.

        Yields:
            Iterable[Audio]: processed audio data
        """
        for _, pipe in self.pipes.items():
            pipe.verbose = verbose
        response_queue = Queue()
        audios = self.loader._to_audios(input)
        results = AudioList[Audio]()
        for i in range(0, len(audios), 10):
            batch_audios = audios[i : i + 10]
            batch_audios = run_component(component=self.loader, audios=batch_audios)
            if len(self.pipe_names) > 0:
                for audio in batch_audios:
                    self.request_queue.put((audio, response_queue))
            else:
                results.extend(batch_audios)
        if len(self.pipe_names) == 0:
            yield from audios
            return

        start = time.perf_counter()
        while True:
            if len(audios) == len(results):
                break
            try:
                audio: Audio = response_queue.get(timeout=timeout)
                if clear:
                    audio.clear()
                yield audio
                results.append(audio)
                response_queue.task_done()
            except Empty:
                logger.error("response queue timeout")
                bad_audios = audios - results
                for audio in bad_audios:
                    if not audio.is_bad:
                        audio.is_bad = True
                        audio.bad_reason = "response queue timeout"
                yield from bad_audios
                break
        end = time.perf_counter()
        spent = max(round(end - start, 2), 1e-5)
        if verbose:
            if not audios.has_bad_audio() and spent > 0 and len(self.pipe_names) > 0:
                logger.info(
                    f"pipeline processed {results.duration_s}s audios, spent {spent}s, speed {round(results.duration_s / spent, 2)}x"
                )

    @validate_call
    def infinite(
        self, input: str | Audio | List[str] | AudioList, verbose: bool = False
    ) -> PipelineResult:
        """run the pipeline in infinite mode which can add tasks and stream results"""
        for _, pipe in self.pipes.items():
            pipe.verbose = verbose
        audios = self.loader._to_audios(input)
        response_queue = Queue()
        result = PipelineResult(
            request_queue=self.request_queue,
            response_queue=response_queue,
            loader=self.loader,
        )
        result.num_inputs = len(audios)
        result.num_outputs = 0
        for i in range(0, len(audios), 10):
            batch_audios = audios[i : i + 10]
            batch_audios = run_component(component=self.loader, audios=batch_audios)
            if len(self.pipe_names) > 0:
                for audio in batch_audios:
                    self.request_queue.put((audio, response_queue))
            else:
                result.num_outputs += len(batch_audios)
        return result

    @validate_call
    def add_pipe(
        self,
        component: str | BaseComponent,
        batch_timeout: float = 0.01,
        batch_size: int | None = 1,
        queue_duration: int = -1,
        verbose: bool = False,
        **config,
    ) -> Self:
        """Add a component to the pipeline

        Args:
            component (str | BaseComponent): the component to add to the pipeline.
            batch_timeout (float, optional): dynamic batch timeout. Defaults to 0.01.
            batch_size (int | None, optional): dynamic batch size. Defaults to 1.
            queue_duration (int, optional): duration of the queue. Defaults to -1. If -1, the queue duration is infinite. if the queue's duration is above this value, the previous component will be blocked.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            **config: the parameters of the component.
        """
        if isinstance(component, str):
            if component == "loader":
                raise ValueError("loader component is reserved")
            if len(self.pipes) == 0:
                input_queue = self.request_queue
            else:
                input_queue = AudioQueue(maxsize=queue_duration)
                pre_pipe = self.pipes[self.pipe_names[-1]]
                pre_pipe.output_queue = input_queue
                pre_pipe.is_last = False
            pipe: Pipe = self._init_pipe(
                component=component,
                is_last=True,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
                input_queue=input_queue,
                verbose=verbose,
                **config,
            )
            pipe.start()
            self.pipes[pipe.name] = pipe
            return self
        elif isinstance(component, BaseComponent):
            if len(self.pipes) == 0:
                input_queue = self.request_queue
            else:
                input_queue = AudioQueue(maxsize=queue_duration)
                pre_pipe = self.pipes[self.pipe_names[-1]]
                pre_pipe.output_queue = input_queue
                pre_pipe.is_last = False
            pipe: Pipe = self._init_pipe(
                component=component,
                is_last=True,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
                input_queue=input_queue,
                verbose=verbose,
                **config,
            )
            pipe.start()
            self.pipes[component.name] = pipe
            return self

    def get_pipe(self, name: str) -> Pipe | None:
        """Get a component from the pipeline

        Args:
            name (str): the name of the component registered in the registry.

        Returns:
            Pipe | None: the component object in the pipeline or None
        """
        return self.pipes.get(name, None)

    def _init_pipe(
        self,
        component: str | BaseComponent,
        verbose: bool = False,
        is_last: bool = True,
        input_queue: AudioQueue = None,
        output_queue: AudioQueue = None,
        batch_timeout: float = 0.01,
        batch_size: int | None = None,
        **config,
    ) -> "Pipe":
        """Initialize a component in the pipeline

        Args:
            component (str | BaseComponent): the component to add to the pipeline. It can be the name of the component registered in the registry or the component object.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            is_last (bool, optional): whether it is the last component. Defaults to True.
            input_queue (AudioQueue, optional): the input queue of the component. Defaults to None.
            output_queue (AudioQueue, optional): the output queue of the component. Defaults to None.
            batch_timeout (float, optional): dynamic batch timeout. Defaults to 0.01.
            batch_size (int | None, optional): dynamic batch size. Defaults to None.

        Returns:
            Pipe: the component object in the pipeline
        """
        if isinstance(component, str):
            _component: BaseComponent = registry.components.get(component)()
            _component = _component.setup(**config)
            pipe = Pipe(
                component=_component,
                verbose=verbose,
                is_last=is_last,
                input_queue=input_queue,
                output_queue=output_queue,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
            )
            return pipe
        elif isinstance(component, BaseComponent):
            pipe = Pipe(
                component=component,
                verbose=verbose,
                is_last=is_last,
                input_queue=input_queue,
                output_queue=output_queue,
                batch_timeout=batch_timeout,
                batch_size=batch_size,
            )
            return pipe

    def remove_pipe(self, name: str) -> Self:
        """Remove a component from the pipeline

        Args:
            name (str): the name of the component.

        Returns:
            Pipeline: the pipeline object
        """
        pipe: Pipe = self.pipes[name]
        if len(self.pipes) == 1:
            self._del_pipe(name)
            return self
        elif pipe.is_last:
            pre_pipe = self.pipes[self.pipe_names[-2]]
            pre_pipe.is_last = True
            pre_pipe.output_queue = None
            self._del_pipe(name)
            return self
        else:
            for i, pipe_name in enumerate(self.pipe_names):
                if pipe_name == name:
                    if i == 0:
                        next_pipe = self.pipes[self.pipe_names[i + 1]]
                        next_pipe.input_queue = self.request_queue
                        self._del_pipe(name)
                        return self
                    else:
                        pre_pipe = self.pipes[self.pipe_names[i - 1]]
                        next_pipe = self.pipes[self.pipe_names[i + 1]]
                        next_pipe.input_queue = pre_pipe.output_queue
                        self._del_pipe(name)
                        return self

    def set_pipe(
        self,
        name: str,
        batch_size: int = 1,
        batch_timeout: float = 0.01,
        **config,
    ) -> Self:
        """Set the dynamic batch size and batch timeout of a component

        Args:
            name (str): the name of the pipe
            batch_size (int, optional): dynamic batch size. Defaults to 1.
            batch_timeout (float, optional): dynamic batch timeout. Defaults to 0.01.
            **config: the parameters of the component.

        Returns:
            Pipeline: the pipeline object
        """
        self.pipes[name].batch_size = batch_size
        self.pipes[name].batch_timeout = batch_timeout
        if config:
            for key, value in config.items():
                if hasattr(self.pipes[name].component, key):
                    setattr(self.pipes[name].component, key, value)
        return self

    def set_loader(self, **kwargs) -> Self:
        """Set the parameters of the loader component

        Returns:
            Self: the pipeline object
        """
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(self.loader, key):
                    setattr(self.loader, key, value)
                else:
                    logger.warning(f"{key} not found in loader")
        return self

    def get_config(self) -> Config:
        """Get the configuration of the pipeline

        Returns:
            Config: the configuration of the pipeline
        """
        data = {
            "pipeline": {
                "@pipelines": "audio_pipeline",
                "loader": self.loader.get_config()["component"],
                "pipes": {},
            }
        }
        for name, pipe in self.pipes.items():
            data["pipeline"]["pipes"][name] = pipe.get_config()["pipe"]
        config = Config(data=data)
        return config

    def save(self, save_dir: str):
        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            import shutil

            shutil.rmtree(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
        config = self.get_config()
        config.to_disk(save_dir / "config.cfg")
        try:
            for name, pipe in self.pipes.items():
                pipe.save(save_dir=save_dir / name)
        except Exception as e:
            import shutil

            shutil.rmtree(save_dir)
            raise e

    def load(self, save_dir: str) -> Self:
        save_dir = Path(save_dir)
        if not save_dir.exists():
            raise FileNotFoundError(f"{save_dir} not found")
        config = Config().from_disk(save_dir / "config.cfg")
        pipeline = registry.resolve(config)["pipeline"]
        self.loader = pipeline.loader
        for name, pipe in pipeline.pipes.items():
            pipe: Pipe = pipe.load(save_dir / name)
            self.add_pipe(
                component=pipe.component,
                batch_timeout=pipe.batch_timeout,
                batch_size=pipe.batch_size,
            )
        return self

    def restart(self):
        while not self.request_queue.empty():
            self.request_queue.get()
            self.request_queue.task_done()
        for _, pipe in self.pipes.items():
            pipe.restart()
        return self

    @property
    def pipe_names(self) -> List[Pipe]:
        """Get the names of the components in the pipeline"""
        names = []
        for _, pipe in self.pipes.items():
            names.append(pipe.name)
        return names

    @property
    def pipe_registry_names(self) -> List[str]:
        """Get the names of the components in the pipeline from the registry

        Returns:
            List[str]: the names of the components in the pipeline
        """
        names = list(self.pipes.keys())
        return names

    def _del_pipe(self, name: str):
        """delete a component from the pipeline"""
        pipe: Pipe = self.pipes[name]
        pipe.stop_event.set()
        pipe.thread.join()
        del self.pipes[name]

    def __del__(self):
        """terminate all threads when delete the object"""
        for name in self.pipe_names:
            pipe = self.pipes[name]
            if pipe.stop_event is not None:
                pipe.stop_event.set()
            if pipe.thread is not None:
                pipe.thread.join()

    def __str__(self) -> str:
        s = "input -> loader -> "
        for name in self.pipe_names:
            s += f"{name} -> "
        return s + "audios"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self.pipes)
