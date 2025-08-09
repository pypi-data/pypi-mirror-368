"""Camera interface for recording and taking pictures using OpenCV."""

import itertools
import sys
import time
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
from loguru import logger

from monocular_path_prediction.config.definitions import DATE_FORMAT, RECORDINGS_DIR


def all_valid(items: Iterable) -> bool:
    """Return True if all items are not None or false.

    :param items: Iterable of values to check.
    :return: True if all items are valid, False otherwise.
    """
    for item in items:
        if item is None:
            return False
        if isinstance(item, np.ndarray):
            continue  # Don't evaluate ndarray as bool; assume not None is valid
        if not item:
            return False
    return True


def get_timestamped_filepath(
    suffix: str, output_dir: Path = RECORDINGS_DIR, prefix: str = ""
) -> Path:
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime(DATE_FORMAT)
    return output_dir / f"{prefix}{timestamp}.{suffix}"


def wait_for_not_none(prompt: str, func: Callable) -> None:
    """Add a spinner to wait for a condition to be true."""
    spinner = itertools.cycle(["⠋", "⠙", "⠸", "⠴", "⠦", "⠇"])
    logger.info(prompt)
    while not all_valid(func()):
        sys.stdout.write(f"\rWaiting {next(spinner)} {prompt}...")
        sys.stdout.flush()
        time.sleep(0.2)
    print()
