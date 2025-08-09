"""Configure the logger."""

import sys
from pathlib import Path

from loguru import logger

from monocular_path_prediction.config.definitions import ENCODING
from monocular_path_prediction.core.utils import get_timestamped_filepath


def setup_logger(stderr_level: str = "INFO", log_level: str = "INFO") -> None:
    """Configure the logger."""
    logger.remove()
    log_filepath = get_timestamped_filepath(
        output_dir=Path("logs"), prefix="pipeline", suffix=".log"
    )
    logger.add(sys.stderr, level=stderr_level)
    logger.add(log_filepath, level=log_level, encoding=ENCODING, enqueue=True)
