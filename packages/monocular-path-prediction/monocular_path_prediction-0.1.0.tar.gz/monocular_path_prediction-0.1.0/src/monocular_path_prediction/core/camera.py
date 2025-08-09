"""Camera interface for recording and taking pictures using OpenCV."""

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from loguru import logger
from PIL import Image

from monocular_path_prediction.config.definitions import RECORDINGS_DIR, CameraConfig
from monocular_path_prediction.core.utils import (
    get_timestamped_filepath,
    wait_for_not_none,
)


class Camera:
    """Camera interface for recording and taking pictures using OpenCV."""

    def __init__(self, config: Optional[CameraConfig] = None):
        """Initialize the camera.

        :param config: Optional camera configuration with index, width, and height.
        """
        self.config = config if config else CameraConfig()
        self.cap = self._initialize_camera()

        assert self.cap is not None, "Failed to initialize camera."

    def _initialize_camera(self) -> cv2.VideoCapture:
        """Try to initialize a camera from the given index.

        :return: An open and working VideoCapture object.
        :raises RuntimeError: If no usable camera is found.
        """
        index = self.config.index
        cap = cv2.VideoCapture(index)

        if not cap.isOpened():
            cap.release()

        # Try reading a frame to confirm it's functional
        logger.info(f"Attempting to open camera at index {index}...")
        wait_for_not_none(prompt="Waiting for camera to initialize.", func=cap.read)
        ret, frame = cap.read()
        if not ret:
            cap.release()

        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera initialized at index {index}: ({width}x{height})")

        return cap

    def take_picture(self) -> Path:
        """Capture a single image and save it."""
        ret, frame = self.cap.read()
        if not ret or frame is None:
            raise RuntimeError("Failed to capture image.")
        filepath = get_timestamped_filepath(
            output_dir=self.config.output_dir, suffix="jpg", prefix="img_"
        )
        cv2.imwrite(str(filepath), frame)
        logger.info(f"Snapshot saved: {filepath}")
        return filepath

    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture and return the current frame from the camera."""
        logger.debug("Capturing camera frame...")
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.warning("Failed to read frame from camera.")
        return frame

    def cleanup(self) -> None:
        """Release resources."""
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera released.")

    def __enter__(self):
        """Enter the context manager and return the camera instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up camera resources."""
        self.cleanup()


def resize_image(image: np.ndarray, new_width: int) -> np.ndarray:
    """Resize an image to a target width while maintaining the same aspect ratio.

    Args:
        image: Input image as a numpy array
        new_width: Target width in pixels (default: 320)

    Returns:
        resized_image

    """
    logger.debug("Resizing image.")
    h, w = image.shape[:2]
    scale_factor = new_width / w
    new_height = int(h * scale_factor)

    # Convert numpy array to PIL Image for resizing
    pil_image = Image.fromarray(image)
    resized_pil = pil_image.resize((new_width, new_height), Image.LANCZOS)
    resized_image = np.array(resized_pil)

    return resized_image


def save_image(image: np.ndarray, output_dir: Path = RECORDINGS_DIR) -> Path:
    """Save an image to a file."""
    filepath = get_timestamped_filepath(
        output_dir=output_dir, suffix="jpg", prefix="img_"
    )
    cv2.imwrite(str(filepath), image)
    logger.info(f"Snapshot saved: {filepath}")
    return filepath
