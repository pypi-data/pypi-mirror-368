from typing import Union, Dict
from pathlib import Path
import yaml


def read_yaml(yaml_path: Union[str, Path]) -> Dict:
    """Read yaml file.

    Args:
        yaml_path (Union[str, Path]): The path of the yaml file.

    Raises:
        FileExistsError: If the file does not exist.

    Returns:
        Dict: The data in the yaml file.
    """
    if not Path(yaml_path).exists():
        raise FileExistsError(f"The {yaml_path} does not exist.")

    with open(str(yaml_path), "rb") as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data
