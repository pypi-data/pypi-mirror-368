from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from fasr.config import Config


FASR_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "fasr" / "checkpoints"


def download(
    repo_id: str,
    revision: str = None,
    cache_dir: str | Path = FASR_DEFAULT_CACHE_DIR,
    endpoint: Literal["modelscope", "huggingface", "hf-mirror"] = "modelscope",
) -> None:
    """Download model from modelscope"""
    cache_dir = Path(cache_dir)
    if endpoint == "hf-mirror":
        from huggingface_hub import snapshot_download

        _ = snapshot_download(
            repo_id=repo_id,
            local_dir=cache_dir / repo_id,
            revision=revision,
            local_dir_use_symlinks=False,
            endpoint="https://hf-mirror.com",
        )
    if endpoint == "huggingface":
        from huggingface_hub import snapshot_download

        _ = snapshot_download(
            repo_id=repo_id,
            local_dir=cache_dir / repo_id,
            revision=revision,
            local_dir_use_symlinks=False,
        )

    elif endpoint == "modelscope":
        from modelscope import snapshot_download

        _ = snapshot_download(model_id=repo_id, cache_dir=cache_dir, revision=revision)


class IOMixin(BaseModel, ABC):
    @abstractmethod
    def save(self, save_dir: str):
        raise NotImplementedError

    @abstractmethod
    def load(self, save_dir: str):
        raise NotImplementedError

    @abstractmethod
    def get_config(self) -> Config:
        raise NotImplementedError


class CheckpointMixin(BaseModel, ABC):
    cache_dir: str | Path = FASR_DEFAULT_CACHE_DIR
    checkpoint: str | None = None
    endpoint: Literal["modelscope", "huggingface", "hf-mirror"] = "hf-mirror"

    @abstractmethod
    def from_checkpoint(self, checkpoint_dir: str, device: str, **kwargs):
        raise NotImplementedError

    def download_checkpoint(self, revision: str = None) -> Path:
        if self.checkpoint is None:
            raise ValueError("checkpoint is None")
        checkpoint_dir = self.cache_dir / self.checkpoint
        if not checkpoint_dir.exists():
            download(
                repo_id=self.checkpoint,
                revision=revision,
                cache_dir=self.cache_dir,
                endpoint=self.endpoint,
            )
        return checkpoint_dir

    @property
    def checkpoint_dir(self) -> Path | None:
        if self.checkpoint is None:
            return None
        return self.cache_dir / self.checkpoint

    @property
    def default_checkpoint_dir(self) -> Path:
        return self.cache_dir / self.checkpoint


def clear_cache(cache_dir: str | Path = FASR_DEFAULT_CACHE_DIR):
    """清空缓存目录

    Args:
        cache_dir (str | Path, optional): 缓存目录. Defaults to DEFAULT_CACHE_DIR = Path.home() / ".cache" / "fasr" / "checkpoints".
    """
    cache_dir = Path(cache_dir)
    if cache_dir.exists():
        for item in cache_dir.iterdir():
            if item.is_dir():
                for sub_item in item.iterdir():
                    sub_item.unlink()
                item.rmdir()
            else:
                item.unlink()
    else:
        cache_dir.mkdir(parents=True)
    return cache_dir
