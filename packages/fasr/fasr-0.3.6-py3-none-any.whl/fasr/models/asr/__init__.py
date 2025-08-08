from lightning_utilities import module_available


from .paraformer import ParaformerForASR
from .sensevoice import SensevoiceForASR
from .seaco_paraformer import SeacoParaformerForASR
from .firered.firered_aed import FireRedAEDForASR

if module_available("dolphin"):
    from .dolphin import DolphinSmallForASR

__all__ = [
    "ParaformerForASR",
    "SensevoiceForASR",
    "SeacoParaformerForASR",
    "FireRedAEDForASR",
    "DolphinSmallForASR",
]
