"""Monocular Surface Normal Estimation Script."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger
from matplotlib import pyplot as plt
from PIL import Image

from monocular_path_prediction import (
    MonocularDepthEstimator,
    NormalEstimator,
    PointCloudGenerator,
    Visualizer,
)
from monocular_path_prediction.config.definitions import (
    DEFAULT_IMAGE_WIDTH,
    RECORDINGS_DIR,
    CameraConfig,
    ModelSize,
)
from monocular_path_prediction.config.setup_logger import setup_logger
from monocular_path_prediction.core import IMUDevice, SerialConfig
from monocular_path_prediction.core.camera import Camera, resize_image, save_image
from monocular_path_prediction.data.point_cloud import SceneData

CAMERA_IMU_SERIAL_PORT = "/dev/tty.usbmodem4F21AFA553C21"


# Default pipeline settings
@dataclass
class PipelineConfig:
    """Configuration for the pipeline."""

    encoder: str = ModelSize.VITS
    camera_config: CameraConfig = field(default_factory=CameraConfig)
    max_point_distance: float = 2.0
    vertical_tolerance_deg: float = 25.0
    normal_sample_rate: int = 100
    show_depth_overlay: bool = True
    show_normals: bool = True
    show_point_cloud: bool = False
    output_dir: Path = RECORDINGS_DIR
    show_results: bool = False


class Pipeline:
    """Main class for running monocular surface normal estimation."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        setup_logger()

        if not config:
            config = PipelineConfig()
        self.config = config
        self.output_dir = config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.depth_estimator = MonocularDepthEstimator(self.config.encoder)
        self.max_distance = self.config.max_point_distance

        self.camera: Optional[Camera] = None
        self.imu: Optional[IMUDevice] = None

    def setup(self) -> None:
        """Initialize camera and IMU."""
        logger.info("Setting up pipeline...")

        self.imu = IMUDevice(config=SerialConfig(port=CAMERA_IMU_SERIAL_PORT))
        self.camera = Camera(config=CameraConfig(index=0))

        logger.info("Pipeline setup complete.")

    def run_loop(self, image_path: Optional[Path]) -> None:
        """Run the pipeline in a loop."""
        while True:
            try:
                self.run(image_path=image_path)
            except KeyboardInterrupt:
                logger.info("Pipeline interrupted.")
                break
            except Exception as err:
                logger.error(f"Pipeline failed: {err}")

    def run(self, image_path: Optional[Path] = None) -> bool:
        """Run the pipeline."""
        logger.info("Running pipeline... Press Ctrl+C to exit.")
        try:
            imu_data, camera_pose = self._wait_for_imu()

            image = self.load_image(image_path)

            focal_length_px = 500.0
            depth_map = self.depth_estimator.infer_depth(image)

            point_cloud = PointCloudGenerator.from_depth_map(
                depth_map=depth_map, image=image, focal_length_px=focal_length_px
            )
            point_cloud.filter_by_distance(self.max_distance)
            point_cloud.down_sample(stride=5)  # Downsample for performance
            point_cloud.rotate(rotation_matrix=camera_pose)

            normals = NormalEstimator.estimate(point_cloud.points)

            if self.config.show_results:
                scene_data = SceneData(
                    image=image,
                    point_cloud=point_cloud,
                    normals=normals,
                    depth_map=depth_map,
                    focal_length_px=focal_length_px,
                )
                self.visualize(scene_data)

            return True

        except Exception as err:
            logger.error(f"Pipeline failed: {err}")
            return False

    def load_image(self, image_path: Optional[Path]) -> np.ndarray:
        """Load an image from a path or either an image from a camera."""
        if image_path:
            image = np.array(Image.open(image_path))
        elif self.camera:
            image = self.camera.capture_frame()
            save_image(image, self.output_dir)
        else:
            msg = "No image or camera initialized."
            logger.warning(msg)
            raise RuntimeError(msg)
        image = resize_image(image, new_width=DEFAULT_IMAGE_WIDTH)
        return image

    def _wait_for_imu(self) -> tuple:
        """Block until valid IMU data and pose are available."""
        if not self.imu:
            raise RuntimeError("IMU not initialized.")

        logger.debug("Waiting for IMU data...")
        imu_data, pose = None, None
        while imu_data is None or pose is None:
            imu_data, pose = self.imu()
        logger.debug(f"IMU data: {imu_data}")
        return imu_data, pose

    def visualize(self, scene_data: SceneData) -> None:
        """Visualize the outputs of the pipeline."""
        try:
            logger.info("Visualizing scene data...")
            viz = Visualizer(scene_data=scene_data, max_distance=self.max_distance)
            viz.plot_normals_on_image()
            viz.plot_point_cloud()
            viz.plot_inverse_depth_image()
            plt.show()
        except KeyboardInterrupt:
            logger.info("Visualizing interrupted.")
        finally:
            plt.close()

    def close(self) -> None:
        """Close all resources cleanly."""
        logger.info("Shutting down pipeline...")
        if self.imu:
            self.imu.close()
        if self.camera:
            self.camera.cleanup()
        logger.info("Pipeline closed.")
