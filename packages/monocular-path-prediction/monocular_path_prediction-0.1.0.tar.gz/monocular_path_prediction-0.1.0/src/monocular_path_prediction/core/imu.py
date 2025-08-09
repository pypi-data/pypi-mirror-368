"""IMU device class."""

import ast
import re
import time
from dataclasses import dataclass
from typing import Optional

from loguru import logger
from numpy import ndarray
from py_imu.madgwick import Madgwick
from py_imu.quaternion import Vector3D
from scipy.spatial.transform import Rotation as Rot

from monocular_path_prediction.config.definitions import (
    DEFAULT_FILTER_GAIN,
    DEFAULT_IMU_DT,
    MEAS_PATTERN,
    TIME_PATTERN,
)
from monocular_path_prediction.core.serial_device import SerialConfig, SerialDevice


@dataclass
class IMUData:
    """Structured IMU data object."""

    timestamp: float
    accel: Vector3D
    gyro: Vector3D
    mag: Optional[Vector3D] = None


class IMUDevice(SerialDevice):
    """IMU device that parses serial lines into structured IMU data."""

    def __init__(self, config: SerialConfig, default_dt: float = DEFAULT_IMU_DT):
        super().__init__(config=config)
        self._latest_data: Optional[IMUData] = None
        self.pose: Optional[ndarray] = None

        freq = 1 / default_dt
        self._madgwick = Madgwick(frequency=freq, gain=DEFAULT_FILTER_GAIN)

        while not self.open():
            logger.info("Waiting for IMU to connect...")

    def _update_pose(self) -> None:
        """Update the estimated pose using the IMU data."""
        if self._latest_data is None:
            return

        self._madgwick.update(
            gyr=self._latest_data.gyro,
            acc=self._latest_data.accel,
            dt=self._latest_data.timestamp - self._latest_data.timestamp,
        )
        quat = self._madgwick.q
        self.pose = Rot.from_quat([quat.x, quat.y, quat.z, quat.w]).as_matrix()

        logger.debug(f"Pose: {self.pose}")

    def _read_loop(self) -> None:
        """Continuously read and parse IMU data in the background."""
        logger.info("Started IMU read thread.")
        while self._running and self._serial and self._serial.is_open:
            try:
                if self._serial.in_waiting > 0:
                    line = self._serial.readline().decode(self.config.decoder).strip()
                    imu_data = self._parse_imu_line(line)
                    if imu_data != self._latest_data:
                        self._latest_data = imu_data
                        self._update_pose()
            except Exception as err:
                logger.warning(f"Failed to read or parse IMU data: {err}")
                if "Device not configured" in str(err):
                    logger.warning("IMU not configured. Disconnecting...")
                    self.close()
                    break
            time.sleep(0.001)

    @staticmethod
    def _parse_imu_line(line: str) -> Optional[IMUData]:
        """Parse a line of IMU data in the given format."""
        try:
            time_match = re.search(TIME_PATTERN, line)
            meas_match = re.search(MEAS_PATTERN, line)
            if not time_match or not meas_match:
                logger.warning(f"Failed to find IMU data match: {line}")
                return None

            timestamp = float(time_match.group(1))
            measurements = ast.literal_eval(meas_match.group(1))
            if not measurements or not isinstance(measurements[0], tuple):
                logger.warning(f"Failed to parse IMU data measurement: {line}")
                return None

            accel_tuple, gyro_tuple = measurements[0]
            accel = Vector3D(*accel_tuple)
            gyro = Vector3D(*gyro_tuple)

            return IMUData(timestamp=timestamp, accel=accel, gyro=gyro)

        except Exception as e:
            logger.error(f"Failed to parse IMU line: {e}")
            return None

    def __call__(self) -> tuple[Optional[IMUData], Optional[ndarray]]:
        """Allow calling the object to get the latest IMU data."""
        return self._latest_data, self.pose


if __name__ == "__main__":  # pragma: no cover
    """Test the IMU device."""
    imu_config = SerialConfig(port="/dev/tty.usbmodem4F21AFA553C21")
    imu = IMUDevice(config=imu_config)
    imu.open()

    try:
        while True:
            data, pose = imu()
            time.sleep(1.0)
    except KeyboardInterrupt:
        logger.info("Interrupted.")
    finally:
        imu.close()
