from fasr.utils.base import IOMixin
from pydantic import ConfigDict


class BaseRuntime(IOMixin):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)

    def run(self, **kwargs):
        raise NotImplementedError

    def save(self, save_dir):
        raise NotImplementedError

    def load(self, save_dir):
        raise NotImplementedError
