import onnxruntime as ort
from typing import List, Optional
import numpy as np
from pathlib import Path
from loguru import logger
from fasr.config import registry, Config
from .base import BaseRuntime


@registry.runtimes.register("ort")
class ORT(BaseRuntime):
    onnx_model_path: str | Path | None = None
    device_id: int | None = None
    intra_op_num_threads: int = 2
    session: ort.InferenceSession | None = None
    verbose: bool = True

    def __call__(self, input_content: List[np.ndarray]) -> np.ndarray:
        return self.run(input_content)

    def run(self, input_content: List[np.ndarray]) -> np.ndarray:
        if self.session is None:
            raise ONNXRuntimeError("ONNXRuntime session is not set.")
        input_dict = dict(zip(self.get_input_names(), input_content))
        try:
            return self.session.run(self.get_output_names(), input_dict)
        except Exception as e:
            print(e)
            raise ONNXRuntimeError("ONNXRuntime inferece failed.") from e

    def get_input_names(
        self,
    ):
        return [v.name for v in self.session.get_inputs()]

    def get_output_names(
        self,
    ):
        return [v.name for v in self.session.get_outputs()]

    def get_character_list(self, key: str = "character"):
        return self.meta_dict[key].splitlines()

    def have_key(self, key: str = "character") -> bool:
        self.meta_dict = self.session.get_modelmeta().custom_metadata_map
        if key in self.meta_dict.keys():
            return True
        return False

    @staticmethod
    def _verify_model(model_path):
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"{model_path} does not exists.")
        if not model_path.is_file():
            raise FileExistsError(f"{model_path} is not a file.")

    def set_session(self, intra_op_num_threads: int):
        self.intra_op_num_threads = intra_op_num_threads
        sess_opt = ort.SessionOptions()
        sess_opt.intra_op_num_threads = intra_op_num_threads
        sess_opt.log_severity_level = 4
        sess_opt.enable_cpu_mem_arena = False
        sess_opt.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_opt.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        EP_list = []
        cuda_ep = "CUDAExecutionProvider"
        cpu_ep = "CPUExecutionProvider"
        if ort.get_device() == "GPU" and cuda_ep in ort.get_available_providers():
            if self.device_id is None:
                device_id = 0
            else:
                device_id = self.device_id
            cuda_provider_options = {
                "device_id": str(device_id),
                "arena_extend_strategy": "kNextPowerOfTwo",
                "cudnn_conv_algo_search": "EXHAUSTIVE",
                "do_copy_in_default_stream": "true",
            }
            EP_list.append((cuda_ep, cuda_provider_options))
            if self.verbose:
                logger.info(f"using onnxruntime-gpu with device_id: {device_id}")
        else:
            cpu_provider_options = {
                "arena_extend_strategy": "kSameAsRequested",
            }
            EP_list.append((cpu_ep, cpu_provider_options))
            if self.verbose:
                logger.info("using onnxruntime-cpu")

        self._verify_model(self.onnx_model_path)
        self.session = ort.InferenceSession(
            self.onnx_model_path, sess_options=sess_opt, providers=EP_list
        )

    def get_config(self) -> Config:
        data = {
            "runtime": {
                "@runtimes": "ort",
                "intra_op_num_threads": self.intra_op_num_threads,
            }
        }
        return Config(data)

    def save(self, save_dir: str = "runtime") -> None:
        import shutil
        from shutil import SameFileError

        save_dir = Path(save_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        model_file = save_dir / "model.onnx"
        try:
            _ = shutil.copy(self.onnx_model_path, model_file)
        except SameFileError:
            pass
        except Exception as e:
            raise ONNXRuntimeError(f"Failed to save model to {model_file}.") from e
        config = self.get_config()
        config.to_disk(Path(save_dir) / "config.cfg")

    def load(self, save_dir: str = "runtime", **kwargs) -> "ORT":
        save_dir = Path(save_dir)
        config = Config().from_disk(save_dir / "config.cfg")
        ort: "ORT" = registry.resolve(config=config)["runtime"]
        ort.onnx_model_path = save_dir / "model.onnx"
        ort.set_session(ort.intra_op_num_threads)
        return ort

    def from_checkpoint(
        self,
        checkpoint_dir: str,
        device_id: Optional[int] = None,
        intra_op_num_threads: int = 2,
        verbose: bool = True,
    ) -> "ORT":
        model_path = Path(checkpoint_dir) / "model.onnx"
        self.onnx_model_path = model_path
        self.device_id = device_id
        self.intra_op_num_threads = intra_op_num_threads
        self.verbose = verbose
        self.set_session(intra_op_num_threads)
        return self


class ONNXRuntimeError(Exception):
    pass
