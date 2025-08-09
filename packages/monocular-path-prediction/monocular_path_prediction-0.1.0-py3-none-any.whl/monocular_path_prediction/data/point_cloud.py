"""Point cloud generation utilities."""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from loguru import logger


@dataclass
class PointCloudData:
    """Class for storing point cloud data."""

    points: np.ndarray  # Shape: (N, 3)
    colors: np.ndarray  # Shape: (N, 3)

    def filter_by_distance(self, max_distance: float) -> None:
        """Return a subset of points and colors within the specified distance."""
        distances = np.linalg.norm(self.points, axis=1)
        mask = distances < max_distance
        self.points = self.points[mask]
        self.colors = self.colors[mask]

    def down_sample(self, stride: int) -> None:
        """Downsample the point cloud using a stride."""
        self.points = self.points[::stride]
        self.colors = self.colors[::stride]

    def rotate(self, rotation_matrix: Optional[np.ndarray]) -> None:
        """Rotate the point cloud using a rotation matrix."""
        if rotation_matrix is None:
            rotation_matrix = np.eye(3)
        logger.info(f"Rotating point cloud by:\n{rotation_matrix}")
        self.points = np.nan_to_num(self.points, nan=0.0, posinf=1e6, neginf=-1e6)
        mask = np.isfinite(self.points).all(axis=1)
        self.points = self.points[mask]
        points = rotation_matrix @ self.points.T
        self.points = points.T


class PointCloudGenerator:
    """Class for generating point clouds from inverse depth maps and images."""

    @staticmethod
    def from_depth_map(
        depth_map: np.ndarray, image: np.ndarray, focal_length_px: float
    ) -> PointCloudData:
        """Generate point cloud from the inverse depth map and image."""
        logger.debug("Creating point cloud from depth map.")
        height_px, width_px = depth_map.shape
        u, v = np.meshgrid(np.arange(width_px), np.arange(height_px))

        center_x, center_y = width_px / 2, height_px / 2
        x = (u - center_x) * depth_map / focal_length_px
        y = (v - center_y) * depth_map / focal_length_px
        z = depth_map

        points_3d = np.stack((x, y, z), axis=-1).reshape(-1, 3)
        colors_rgb = image.reshape(-1, 3)
        valid = z.reshape(-1) > 0

        return PointCloudData(points=points_3d[valid], colors=colors_rgb[valid])


@dataclass
class SceneData:
    """Class for storing scene data."""

    image: np.ndarray
    point_cloud: PointCloudData
    normals: np.ndarray
    depth_map: np.ndarray
    focal_length_px: float
