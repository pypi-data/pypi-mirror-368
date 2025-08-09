"""Definitions for the package."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Default encoding
ENCODING = "utf-8"
RECORDINGS_DIR: Path = Path("recordings")
DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"

# Default plot settings
FIG_SIZE = (10, 8)  # inches

# Set Numpy print options
np.set_printoptions(precision=3, floatmode="fixed", suppress=True)

# settings for the Depth Anything V2 models
PRETRAINED_MODEL_DIR = "checkpoints"
MODEL_EXTENSION = ".pth"


@dataclass
class ModelSize:
    """Define the depth estimation model sizes."""

    VITS = "vits"
    VITB = "vitb"
    VITL = "vitl"


MODEL_CONFIGS = {
    ModelSize.VITS: {
        "encoder": "vits",
        "features": 64,
        "out_channels": [48, 96, 192, 384],
    },
    ModelSize.VITB: {
        "encoder": "vitb",
        "features": 128,
        "out_channels": [96, 192, 384, 768],
    },
    ModelSize.VITL: {
        "encoder": "vitl",
        "features": 256,
        "out_channels": [256, 512, 1024, 1024],
    },
}

DEFAULT_IMAGE_WIDTH = 320
DEFAULT_IMAGE_HEIGH = 240


# Default camera settings
@dataclass
class CameraConfig:
    """Configuration for the camera."""

    output_dir: Path = RECORDINGS_DIR
    width: int = DEFAULT_IMAGE_WIDTH
    height: int = DEFAULT_IMAGE_HEIGH
    focal_length_px: float = 500
    cx: float = width / 2.0
    cy: float = height / 2.0
    fps: int = 5
    index: int = 0


# Patterns
TIME_PATTERN = r"Time:\s*([0-9.]+)"
MEAS_PATTERN = r"Measurements:\s*(\[.*\])"
DEFAULT_IMU_DT: float = 0.01
DEFAULT_FILTER_GAIN: float = 0.033
