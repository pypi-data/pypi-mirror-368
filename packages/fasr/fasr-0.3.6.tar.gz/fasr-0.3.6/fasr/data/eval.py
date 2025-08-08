from __future__ import annotations
from pathlib import Path
from typing import Literal, Generator, Any
from typing_extensions import Self

from docarray import BaseDoc, DocList
from docarray.utils.filter import filter_docs
from pydantic import Field, model_validator

from .audio import Audio, AudioList, AudioChannel


class AudioEvalExample(BaseDoc):
    """Audio example object that represents an example of input and target audio."""

    x: Audio = Field(..., description="Input audio.")
    y: Audio = Field(..., description="Target audio.")
    is_badcase: bool = Field(False, description="whether the example is a badcase")

    @model_validator(mode="after")
    def validate_audio_example(self):
        if len(self.x.channels) != len(self.y.channels):
            raise ValueError(
                "Input and target audio must have the same number of channels."
            )
        return self

    def char_error_rate(
        self,
        ignore_space: bool = True,
        ignore_punc: bool = True,
        normalize: bool = False,
    ) -> float:
        """Compute the character error rate (CER) between the input and target audio on all the channels.

        Args:
            ignore_space (bool, optional): Whether to ignore space. Defaults to True.
            ignore_punc (bool, optional): Whether to ignore punctuation. Defaults
            normalize (bool, optional): Whether to normalize the text. Defaults to False.
        Returns:
            float: Character error rate.

        """
        from fasr.utils.metric import compute_char_error_rate

        cer = 0
        for i in range(len(self.x.channels)):
            x = self.x.channels[i].text
            y = self.y.channels[i].text
            err = compute_char_error_rate(
                x=x,
                y=y,
                ignore_space=ignore_space,
                ignore_punc=ignore_punc,
                normalize=normalize,
            )
            if err > 0:
                self.is_badcase = True
            cer += err

        return round(cer, 4)

    def clear_waveform(self) -> Self:
        """Clear the waveform of the input and target audio."""
        self.x.clear_waveform()
        self.y.clear_waveform()
        return self


class AudioEvalResult(DocList):
    @property
    def x(self) -> AudioList[Audio]:
        return AudioList(docs=[example.x for example in self])

    @property
    def y(self) -> AudioList[Audio]:
        return AudioList(docs=[example.y for example in self])

    def add_example(self, x: Audio | AudioList, y: Audio | AudioList) -> Self:
        """Add an audio example to the evaluation."""
        if isinstance(x, Audio):
            x = AudioList([x])
        if isinstance(y, Audio):
            y = AudioList([y])
        if len(x) != len(y):
            raise ValueError(
                "Input and target audio must have the same number of channels."
            )
        for x_audio, y_audio in zip(x, y):
            self.append(AudioEvalExample(x=x_audio, y=y_audio))
        return self

    def char_error_rate(
        self,
        ignore_space: bool = True,
        ignore_punc: bool = True,
        normalize: bool = False,
    ) -> float:
        """Compute the character error rate (CER) between the input and target audio on all the channels.
        Args:
            ignore_space (bool, optional): Whether to ignore space. Defaults to True.
            ignore_punc (bool, optional): Whether to ignore punctuation. Defaults to True.
            normalize (bool, optional): Whether to normalize the text. Defaults to False.
        Returns:
            float: Character error rate.
        """

        cer = 0
        for audio_example in self:
            audio_example: AudioEvalExample
            cer += audio_example.char_error_rate(
                ignore_space=ignore_space,
                ignore_punc=ignore_punc,
                normalize=normalize,
            )

        return round(cer / len(self), 6)

    def save_binary(
        self,
        file: str | Path,
        protocol: Literal[
            "protobuf", "pickle", "json", "json-array", "protobuf-array", "pickle-array"
        ] = "protobuf",
        compress: Literal["lz4", "bz2", "lzma", "zlib", "gzip"] | None = None,
        show_progress: bool = False,
        clear_waveform: bool = True,
    ) -> None:
        """Save the audio list to a binary file.

        Args:
            file (str | Path): Path to the binary file.
            protocol (Literal[ &quot;protobuf&quot;, &quot;pickle&quot;, &quot;json&quot;, &quot;json, optional): the protocol to use. Defaults to &quot;protobuf&quot;.
            compress (Literal[&quot;lz4&quot;, &quot;bz2&quot;, &quot;lzma&quot;, &quot;zlib&quot;, &quot;gzip&quot;] | None, optional): the compression method to use. Defaults to None.
            show_progress (bool, optional): whether to show progress bar. Defaults to False.
            filter_bad (bool, optional): whether to filter bad audio files. Defaults to False.
            clear_waveform: whether clear the waveform.
        """
        if clear_waveform:
            for example in self:
                example: AudioEvalExample
                x_texts = []
                for channel in example.x.channels:
                    channel: AudioChannel
                    x_texts.append(channel.text)
                example.clear_waveform()
                example.x.clear_text()
                for i, channel in enumerate(example.x.channels):
                    channel.raw_text = x_texts[i]
        return super().save_binary(file, protocol, compress, show_progress)

    @classmethod
    def load_binary(
        cls,
        file: str | bytes | Path,
        protocol: Literal[
            "protobuf", "pickle", "json", "json-array", "protobuf-array", "pickle-array"
        ] = "protobuf",
        compress: Literal["lz4", "bz2", "lzma", "zlib", "gzip"] | None = None,
        show_progress: bool = False,
        streaming: bool = False,
    ) -> DocList[Audio] | Generator[Any, None, None]:
        """Load the audio list from a binary file.

        Args:
            file (str | Path): Path to the binary file.
            show_progress (bool, optional): whether to show progress bar. Defaults to False.

        Returns:
            AudioList: Audio list.
        """
        docs = DocList[AudioEvalExample].load_binary(
            file=file,
            protocol=protocol,
            compress=compress,
            show_progress=show_progress,
            streaming=streaming,
        )
        if isinstance(docs, Generator):
            return docs
        return AudioEvalResult[AudioEvalExample](docs=docs)

    def get_badcase(self) -> AudioEvalResult[AudioEvalExample]:
        query = {"is_badcase": {"$eq": True}}
        return AudioEvalResult[AudioEvalExample](
            docs=filter_docs(docs=self, query=query)
        )
