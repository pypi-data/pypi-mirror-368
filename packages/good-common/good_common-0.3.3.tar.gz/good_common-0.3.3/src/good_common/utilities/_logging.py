from contextlib import contextmanager
from time import perf_counter

from loguru import logger


@contextmanager
def catchtime(name: str):
    """
    Derived from # https://stackoverflow.com/questions/33987060/python-context-manager-that-measures-time
    """
    logger.info(f"{name}: starting...")
    start = perf_counter()
    yield lambda: perf_counter() - start
    logger.info(f"\t\t complete in {perf_counter() - start:.3f} seconds")


def human_readable_bytes(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} YB"
