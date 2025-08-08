from pathlib import Path
from typing import List
from random import choices


def random_hotwords(n: int) -> List[str]:
    """Generate random hotwords.

    Args:
        n (int): The number of hotwords.

    Returns:
        List[str]: The list of hotwords.
    """
    hotwords_file = Path(__file__).parent.parent / "asset" / "example" / "hotwords.txt"
    with open(hotwords_file, "r") as f:
        hotwords = f.readlines()
    hotwords = choices(hotwords, k=n)
    return [hotword.strip() for hotword in hotwords]
