import time
from typing import Callable
from loguru import logger
from functools import wraps


def timer(
    tag: str,
    round_num: int = 2,
    is_class: bool = True,
    log_time: bool = True,
    accumulate_time: bool = False,
):
    def outter(func: Callable):
        if is_class:

            @wraps(func)
            def wrapper(self, *args, **kwargs):
                start = time.perf_counter()
                res = func(self, *args, **kwargs)
                end = time.perf_counter()
                spent = round(end - start, round_num)
                if log_time:
                    logger.info(f"{tag} run in {spent} seconds")
                if hasattr(self, "timer_data"):
                    if accumulate_time:
                        if self.timer_data is None:
                            self.timer_data = {}
                        if tag in self.timer_data:
                            self.timer_data[tag] += spent
                        else:
                            self.timer_data[tag] = spent
                    else:
                        self.timer_data[tag] = spent
                return res

            return wrapper

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                res = func(*args, **kwargs)
                end = time.perf_counter()
                spent = round(end - start, round_num)
                if log_time:
                    logger.info(f"{tag} run in {spent} seconds")
                return res

            return wrapper

    return outter
