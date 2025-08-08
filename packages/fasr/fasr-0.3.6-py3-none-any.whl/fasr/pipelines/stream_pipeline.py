from __future__ import annotations
from pydantic import validate_call, ConfigDict, Field, model_validator
from docarray import BaseDoc
from fasr.components.stream.base import BaseStreamComponent
from fasr.data import AudioChunk, AudioChunkList, Waveform
from fasr.config import registry, Config
from fasr.utils.base import IOMixin
from typing import List
from typing_extensions import Self
from collections import OrderedDict
from loguru import logger
from queue import Queue, Empty
from pathlib import Path
import time
import threading

from .audio_pipeline import AudioQueue


def run_component(
    component: BaseStreamComponent, audio_chunk: AudioChunk
) -> AudioChunk:
    """Run a component to process the audio chunk

    Args:
        component (BaseStreamComponent): the component to process the audio chunk
        audio_chunk (AudioChunk): the audio chunk to process

    Returns:
        AudioChunk: the processed audio chunk
    """
    start = time.perf_counter()
    audio_chunk: AudioChunk = audio_chunk | component
    end = time.perf_counter()
    spent = end - start
    if audio_chunk.spent_time is None:
        audio_chunk.spent_time = {}
    if audio_chunk.spent_time.get(component.name) is None:
        audio_chunk.spent_time[component.name] = spent
    else:
        audio_chunk.spent_time[component.name] += spent
    audio_chunk.spent_time[component.name] = round(
        audio_chunk.spent_time[component.name], 3
    )
    return audio_chunk


class Pipe(IOMixin):
    """Pipe is a component in the pipeline that can process the audio chunk"""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    component: BaseStreamComponent | None = Field(
        None, description="the component to process the audio"
    )
    verbose: bool = Field(False, description="whether to print detailed logs")
    input_queue: Queue | None = None
    output_queue: Queue | None = None
    is_last: bool = Field(True, description="whether it is the last component")
    stop_event: threading.Event | None = Field(None, description="stop event")
    thread: threading.Thread | None = Field(default=None, description="thread object")

    @model_validator(mode="after")
    def validate_stop_event(self):
        if self.stop_event is None:
            self.stop_event = threading.Event()
        return self

    def predict(self, audio_chunk: AudioChunk) -> AudioChunk:
        """Predict the audio data"""
        audio_chunk = run_component(component=self.component, audio_chunk=audio_chunk)
        return audio_chunk

    def run_loop(self):
        while not self.stop_event.is_set():
            item = self.input_queue.get()
            audio_chunk, response_queue = item
            start = time.perf_counter()
            _ = self.predict(audio_chunk=audio_chunk)
            end = time.perf_counter()
            spent = round(end - start, 2)  # noqa
            if self.is_last or self.output_queue is None:
                response_queue: Queue
                response_queue.put(audio_chunk)
            else:
                self.output_queue.put((audio_chunk, response_queue))
                self.input_queue.task_done()

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
        component: BaseStreamComponent = registry.resolve(component_config)["component"]
        self.component = component.load(component_dir)
        return self

    @property
    def name(self) -> str | None:
        if self.component is None:
            return None
        return self.component.name


@registry.pipelines.register("stream_pipeline")
class StreamPipeline(IOMixin):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    pipes: OrderedDict[str, Pipe] | None = Field(
        default=None, description="the components in the pipeline"
    )
    request_queue: Queue | None = Field(
        default=Queue(), description="the request queue"
    )

    @model_validator(mode="after")
    def validate_pipes(self):
        if self.pipes is None:
            self.pipes = OrderedDict()
        if self.request_queue is None:
            self.request_queue = Queue()
        return self

    def create_stream(self) -> AudioStream:
        return AudioStream(request_queue=self.request_queue)

    @validate_call
    def add_pipe(
        self,
        component: str | BaseStreamComponent,
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
            if len(self.pipes) == 0:
                input_queue = self.request_queue
            else:
                input_queue = Queue()
                pre_pipe = self.pipes[self.pipe_names[-1]]
                pre_pipe.output_queue = input_queue
                pre_pipe.is_last = False
            pipe: Pipe = self._init_pipe(
                component=component,
                is_last=True,
                input_queue=input_queue,
                verbose=verbose,
                **config,
            )
            pipe.start()
            self.pipes[pipe.name] = pipe
            return self
        elif isinstance(component, BaseStreamComponent):
            if len(self.pipes) == 0:
                input_queue = self.request_queue
            else:
                input_queue = AudioQueue()
                pre_pipe = self.pipes[self.pipe_names[-1]]
                pre_pipe.output_queue = input_queue
                pre_pipe.is_last = False
            pipe: Pipe = self._init_pipe(
                component=component,
                is_last=True,
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
        component: str | BaseStreamComponent,
        verbose: bool = False,
        is_last: bool = True,
        input_queue: AudioQueue = None,
        output_queue: AudioQueue = None,
        **config,
    ) -> "Pipe":
        """Initialize a component in the pipeline

        Args:
            component (str | BaseComponent): the component to add to the pipeline. It can be the name of the component registered in the registry or the component object.
            verbose (bool, optional): whether to print detailed logs. Defaults to False.
            is_last (bool, optional): whether it is the last component. Defaults to True.
            input_queue (AudioQueue, optional): the input queue of the component. Defaults to None.
            output_queue (AudioQueue, optional): the output queue of the component. Defaults to None.

        Returns:
            Pipe: the component object in the pipeline
        """
        if isinstance(component, str):
            _component: BaseStreamComponent = registry.stream_components.get(
                component
            )()
            _component = _component.setup(**config)
            pipe = Pipe(
                component=_component,
                verbose=verbose,
                is_last=is_last,
                input_queue=input_queue,
                output_queue=output_queue,
            )
            return pipe
        elif isinstance(component, BaseStreamComponent):
            pipe = Pipe(
                component=component,
                verbose=verbose,
                is_last=is_last,
                input_queue=input_queue,
                output_queue=output_queue,
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

    def clear_state(self, stream_id: str) -> Self:
        for _, pipe in self.pipes.items():
            pipe.component.clear_state(stream_id)
        return self

    def get_config(self) -> Config:
        """Get the configuration of the pipeline

        Returns:
            Config: the configuration of the pipeline
        """
        pass

    def save(self, save_dir: str):
        pass

    def load(self, save_dir: str) -> Self:
        pass

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
        s = "input -> "
        for name in self.pipe_names:
            s += f"{name} -> "
        return s + "output"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self.pipes)


class AudioStream(BaseDoc):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    request_queue: Queue | None
    response_queue: Queue = Queue()
    chunks: AudioChunkList = AudioChunkList()

    @validate_call
    def process_chunk(
        self,
        waveform: Waveform,
        is_last: bool,
        timeout: float | None = None,
        verbose: bool = False,
    ) -> AudioChunk:
        """pass the audio data through the pipeline"""
        audio_chunk = AudioChunk(stream_id=self.id, waveform=waveform, is_last=is_last)
        response_queue = self.response_queue
        start = time.perf_counter()
        self.request_queue.put((audio_chunk, response_queue))
        try:
            audio_chunk: AudioChunk = response_queue.get(timeout=timeout)
        except Empty:
            logger.error("process chunk timeout")
            audio_chunk.is_bad = True
            audio_chunk.bad_reason = "process chunk timeout"
        response_queue.task_done()
        end = time.perf_counter()
        spent = max(round(end - start, 2), 1e-5)
        if verbose:
            logger.info("process chunk spent time: {}s", spent)
        return audio_chunk
