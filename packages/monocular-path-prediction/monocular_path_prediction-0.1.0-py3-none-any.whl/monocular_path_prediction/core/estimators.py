"""Monocular depth and normal estimation algorithms."""

import os
from typing import Optional

import cv2
import numpy as np
import torch
from depth_anything_v2.dpt import DepthAnythingV2
from loguru import logger
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

from monocular_path_prediction.config.definitions import (
    MODEL_CONFIGS,
    MODEL_EXTENSION,
    PRETRAINED_MODEL_DIR,
)


class MonocularDepthEstimator:
    """Class for estimating inverse depth maps from images."""

    def __init__(self, encoder: str, device: Optional[str] = None):
        if device is None:
            self.device = (
                "cuda"
                if torch.cuda.is_available()
                else "mps"
                if torch.backends.mps.is_available()
                else "cpu"
            )
        else:
            self.device = device
        logger.info(f"Using device: {self.device}")

        self.model = self.load_model(encoder)

    def load_model(self, encoder: str):
        """Load the model for the specified encoder."""
        checkpoint_path = os.path.join(
            PRETRAINED_MODEL_DIR, f"depth_anything_v2_{encoder}{MODEL_EXTENSION}"
        )
        logger.info(f"Loading model for encoder: {encoder}")

        if not os.path.exists(checkpoint_path):
            msg = f"Checkpoint {checkpoint_path} not found."
            logger.error(msg)
            raise FileNotFoundError(msg)

        model = DepthAnythingV2(**MODEL_CONFIGS[encoder])
        model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
        return model.to(self.device).eval()

    @staticmethod
    def convert_to_bgr(image: np.ndarray) -> np.ndarray:
        """Convert RGB to BGR if needed (OpenCV uses BGR)."""
        if len(image.shape) == 3 and image.shape[2] == 3:
            if not isinstance(image, np.ndarray):
                image = np.array(image)
            # Check if an image is in RGB format (this is a heuristic)
            if image[0, 0, 0] > image[0, 0, 2]:  # If R > B, likely RGB
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def infer_inverse_depth(self, image: np.ndarray) -> np.ndarray:
        """Infer an inverse depth map from an image.

        Args:
            image: a preloaded image as a numpy array

        Returns:
            Inverse depth map as a numpy array

        """
        # Convert RGB to BGR if needed (OpenCV uses BGR)
        image = self.convert_to_bgr(image)
        return self.model.infer_image(image)

    def infer_depth(self, image: np.ndarray) -> np.ndarray:
        """Infer an inverse depth map from an image."""
        image = self.convert_to_bgr(image)
        inv_depth_map = self.model.infer_image(image)
        depth = 1.0 / (inv_depth_map + 1e-6)
        return depth


class NormalEstimator:
    """Class for estimating surface normals from point clouds."""

    @staticmethod
    def estimate(points: np.ndarray, k: int = 20) -> np.ndarray:
        """Estimate surface normals from point cloud."""
        neighbors = NearestNeighbors(n_neighbors=k + 1, algorithm="kd_tree").fit(points)
        _, indices = neighbors.kneighbors(points)

        normals = np.zeros_like(points)

        for i, neighbors in tqdm(
            enumerate(indices),
            total=len(points),
            desc="Estimating Normals",
            leave=False,
        ):
            neighbor_pts = points[neighbors[1:]]
            centroid = neighbor_pts.mean(axis=0)
            centered = neighbor_pts - centroid
            cov = centered.T @ centered
            _, _, vh = np.linalg.svd(cov)
            normal = vh[-1]
            normal /= np.linalg.norm(normal)

            # Flip normals to face toward the sensor
            to_sensor = -points[i]
            if np.dot(normal, to_sensor) < 0:
                normal *= -1

            normals[i] = normal

        return normals
