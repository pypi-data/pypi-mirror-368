"""Serial device interface for reading and writing data to a serial port."""

import threading
import time
from dataclasses import dataclass
from typing import Optional

import serial
from loguru import logger


@dataclass
class SerialConfig:
    """Class for configuring a serial device."""

    port: str
    baud_rate: int = 115200
    timeout: float = 0.1
    decoder: str = "utf-8"
    loop_delay: float = 0.001


class SerialDevice:
    """Class for managing a serial device connection with background reading."""

    def __init__(self, config: SerialConfig):
        """Initialize the serial device interface.

        :param config: Serial port configuration.
        """
        self.config = config
        self._serial: Optional[serial.Serial] = None

        self._latest_line: Optional[str] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self.is_connected = False

    def open(self) -> bool:
        """Open the serial connection and start background reading."""
        if self._serial and self._serial.is_open:
            logger.warning(f"Serial port {self.config.port} already open.")
            self.is_connected = True
            return self.is_connected
        try:
            self._serial = serial.Serial(
                self.config.port, self.config.baud_rate, timeout=self.config.timeout
            )
            self._running = True
            self._thread.start()
            logger.info(f"Opened serial port: {self.config.port}")
            self.is_connected = True
        except serial.SerialException as err:
            self.is_connected = False
            logger.warning(err)
            time.sleep(1.0)
        return self.is_connected

    def close(self) -> None:
        """Stop the background thread and close the serial connection."""
        self._running = False
        self._thread.join()
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info(f"Closed serial port: {self.config.port}")

    def read_line(self) -> Optional[str]:
        """Return the most recent line received from the serial device.

        :return: Latest line or None if nothing received yet
        """
        with self._lock:
            return self._latest_line

    def _read_loop(self) -> None:
        """Continuously read lines from the serial device in a background thread."""
        logger.info("Started serial read thread.")
        while self._running and self._serial and self._serial.is_open:
            try:
                if self._serial.in_waiting > 0:
                    line = self._serial.readline().decode(self.config.decoder).strip()
                    with self._lock:
                        self._latest_line = line
            except Exception as e:
                logger.warning(f"Failed to read from serial port: {e}")
            time.sleep(self.config.loop_delay)  # Prevent CPU overuse


def main():
    """Test the serial device interface."""
    config = SerialConfig(port="/dev/tty.usbmodem4F21AFA553C21")
    serial_device = SerialDevice(config)
    serial_device.open()
    try:
        while True:
            line = serial_device.read_line()
            if line:
                logger.info(f"[Received] {line}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        serial_device.close()


if __name__ == "__main__":
    main()
