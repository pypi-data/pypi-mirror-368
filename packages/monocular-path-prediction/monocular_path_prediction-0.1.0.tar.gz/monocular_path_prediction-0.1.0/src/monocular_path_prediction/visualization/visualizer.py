"""Visualization utilities for monocular path prediction."""

import matplotlib.pyplot as plt
import numpy as np

from monocular_path_prediction.config import FIG_SIZE
from monocular_path_prediction.data.point_cloud import SceneData

EPSILON = 1e-6


def plot_unit_axes(ax: plt.Axes) -> None:
    """Plot unit axes on a 3D plot."""
    length = 0.1
    colors = ["r", "g", "b"]

    x, y, z = 0.0, 0.0, 0.0
    for ii in range(3):
        uvw = [0.0, 0.0, 0.0]
        uvw[ii] = length
        ax.quiver(x, y, z, uvw[0], uvw[1], uvw[2], color=colors[ii])


class Visualizer:
    """Class for visualizing surface normals and point clouds."""

    def __init__(self, scene_data: SceneData, max_distance: float) -> None:
        self.scene_data = scene_data
        self.max_distance = max_distance
        self.max_points = 20000

    def plot_normals_on_image(self) -> None:
        """Plot vertical normals overlaid on the image with masked inverse depth."""
        focal_length_px = self.scene_data.focal_length_px

        sample_rate = 50
        sample = slice(0, len(self.scene_data.point_cloud.points), sample_rate)
        pts_sampled = self.scene_data.point_cloud.points[sample]
        nrm_sampled = self.scene_data.normals[sample]

        vertical_mask = np.abs(nrm_sampled[:, 1]) > 0.9
        pts_sampled = pts_sampled[vertical_mask]
        nrm_sampled = nrm_sampled[vertical_mask]

        x, y, z = pts_sampled[:, 0], pts_sampled[:, 1], pts_sampled[:, 2]

        h, w = self.scene_data.depth_map.shape
        cx, cy = w / 2, h / 2
        u = (x * focal_length_px / z) + cx
        v = (y * focal_length_px / z) + cy

        normal_end = pts_sampled + nrm_sampled * 0.05
        x2, y2, z2 = normal_end[:, 0], normal_end[:, 1], normal_end[:, 2]
        u2 = (x2 * focal_length_px / z2) + cx
        v2 = (y2 * focal_length_px / z2) + cy

        du = u2 - u
        dv = v2 - v

        depth = self.scene_data.depth_map
        depth_mask = (depth > 0.0) & (depth < self.max_distance)

        plt.figure(figsize=FIG_SIZE)
        plt.imshow(self.scene_data.image)
        plt.imshow(np.ma.masked_where(~depth_mask, depth), alpha=0.8)
        plt.quiver(
            u,
            v,
            du,
            dv,
            color="cyan",
            angles="xy",
            scale_units="xy",
            scale=10.0,
            width=0.002,
        )
        plt.title("Surface Normals and Masked Inverse Depth Overlaid on Image")
        plt.axis("off")
        plt.tight_layout()

    def plot_point_cloud(self):
        """Plot 3D point cloud with color."""
        point_cloud = self.scene_data.point_cloud
        fig = plt.figure(figsize=FIG_SIZE)
        ax = fig.add_subplot(111, projection="3d")

        stride = int(np.ceil(point_cloud.points.shape[0] / self.max_points))
        sample_points = point_cloud.points[::stride]
        sample_colors = point_cloud.colors[::stride] / 255.0
        ax.scatter(
            sample_points[:, 0],
            sample_points[:, 1],
            sample_points[:, 2],
            c=sample_colors,
            s=1,
        )
        plot_unit_axes(ax)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("3D Point Cloud")
        ax.view_init(elev=-90, azim=-90, roll=0)
        ax.set_box_aspect([1, 1, 1])
        ax.set_aspect("equal")
        plt.tight_layout()

    def plot_inverse_depth_image(self) -> None:
        """Plot inverse depth map."""
        plt.figure(figsize=FIG_SIZE)
        plt.imshow(1 / self.scene_data.depth_map)
        plt.title("Inverse Depth Map")
        plt.axis("off")
