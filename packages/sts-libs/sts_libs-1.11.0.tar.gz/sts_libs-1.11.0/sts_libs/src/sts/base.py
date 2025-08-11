# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base device classes.

This module provides base classes for all device types:
- Device: Base class for all devices
- NetworkDevice: Network-capable devices
- StorageDevice: Storage devices
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from sts.utils.cmdline import run
from sts.utils.errors import DeviceNotFoundError

# Constants
BYTES_PER_UNIT = 1024  # Number of bytes in each unit (KB, MB, etc.)
UDEV_SETTLE_TIMEOUT = 60  # Maximum time to wait for udev to settle (seconds)


@dataclass
class Device:
    """Base class for all devices.

    This class provides common functionality for all device types:
    - Device identification
    - Path handling
    - Basic operations
    - udev synchronization

    Args:
        path: Device path (optional, e.g. '/dev/sda', '/sys/class/net/eth0')
        name: Device name (optional, e.g. 'sda')

    Raises:
        DeviceNotFoundError: If device does not exist
        DeviceError: If device cannot be accessed

    Example:
        ```python
        device = Device('/dev/sda')
        ```
    """

    path: Path | str | None = None
    name: str | None = None
    validate_on_init: bool = field(init=False, default=True)

    # Standard Linux device paths
    DEV_PATH: ClassVar[Path] = Path('/dev')  # Device nodes (e.g. /dev/sda)
    SYS_PATH: ClassVar[Path] = Path('/sys')  # Sysfs device info (e.g. /sys/block/sda)

    def __post_init__(self) -> None:
        """Initialize device.

        Validates device exists and can be accessed.

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Convert path to Path if provided
        if self.path:
            self.path = Path(self.path)
            if not self.name:
                self.name = self.path.name
            if self.validate_on_init:
                self.validate_device_exists()

    def validate_device_exists(self) -> None:
        """Validate that the device exists on the system."""
        if self.path and not Path(self.path).exists():
            raise DeviceNotFoundError(f'Device not found: {self.path}')

    def wait_udev(self, timeout: int = UDEV_SETTLE_TIMEOUT) -> bool:
        """Wait for udev to settle.

        This method waits for udev to finish processing device events.
        This is useful after device creation or modification to ensure
        all device nodes and symlinks are created.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if udev settled, False if timeout reached

        Example:
            ```python
            device = Device('/dev/sda')
            device.wait_udev()
            True
            ```
        """
        # First try udevadm settle - this is faster but may fail if udev is busy
        result = run('udevadm settle')
        if result.succeeded:
            return True

        # If settle failed, poll for device existence
        # This is slower but more reliable, especially for slow devices
        if not self.path:
            return False

        start_time = time.time()
        while time.time() - start_time < timeout:
            if Path(self.path).exists():
                return True
            time.sleep(0.1)  # Small sleep to avoid busy waiting

        logging.warning(f'Timeout waiting for udev to settle on {self.path}')
        return False

    def __str__(self) -> str:
        """Return string representation of device."""
        return f'{self.__class__.__name__}({self.path or "unknown"})'


@dataclass
class NetworkDevice(Device):
    """Network-capable device.

    This class provides functionality for network-capable devices:
    - IP address management
    - Port management
    - Network operations

    Args:
        path: Device path (optional, e.g. '/sys/class/net/eth0')
        ip: IP address (optional)
        port: Port number (optional)

    Example:
        ```python
        device = NetworkDevice('/sys/class/net/eth0', '192.168.1.1', 80)
        ```
    """

    ip: str | None = None
    port: int | None = field(default=None)

    # Network devices are managed through sysfs
    NET_PATH: ClassVar[Path] = Path('/sys/class/net')


@dataclass
class StorageDevice(Device):
    """Storage device.

    This class provides functionality for storage devices:
    - Size information
    - Model information
    - Storage operations

    Args:
        path: Device path (optional, e.g. '/dev/sda')
        size: Device size in bytes (optional)
        model: Device model (optional)

    Example:
        ```python
        device = StorageDevice('/dev/sda', 1000000000000, 'Samsung SSD 970 EVO')
        ```
    """

    size: int | None = None
    model: str | None = None

    # Block devices are managed through sysfs block subsystem
    BLOCK_PATH: ClassVar[Path] = Path('/sys/block')

    def __post_init__(self) -> None:
        """Initialize storage device.

        Validates size is positive if provided.

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
            ValueError: If size is invalid
        """
        # Initialize parent class first
        super().__post_init__()

        # Basic size validation - negative sizes are impossible
        if self.size is not None and self.size < 0:
            msg = f'Invalid size: {self.size}'
            raise ValueError(msg)

    @property
    def size_human(self) -> str:
        """Get human-readable size.

        Returns:
            Size string (e.g. '1.0 TB') or 'Unknown' if size is not available

        Example:
            ```python
            device = StorageDevice('/dev/sda', 1000000000000)
            device.size_human
            '1.0 TB'
            ```
        """
        if self.size is None:
            return 'Unknown'

        # Convert bytes to human readable format using binary prefixes
        # (1024-based: KiB, MiB, etc. but displayed as KB, MB for simplicity)
        size = float(self.size)
        for unit in ('B', 'KB', 'MB', 'GB', 'TB', 'PB'):
            if size < BYTES_PER_UNIT:
                return f'{size:.1f} {unit}'
            size /= BYTES_PER_UNIT
        return f'{size:.1f} EB'

    def check_sector_zero(self) -> bool:
        """Check the content of sector zero (first 512 bytes) of a block device.

        Returns:
            bool: `True` if the sector zero is successfully read and has the correct size,
                  `False` otherwise.
        """
        if not self.path:
            logging.warning('Cannot check sector zero: path is not set')
            return False
        try:
            with Path(self.path).open('rb') as f:
                # Read the first 512 bytes, which represent sector zero
                sector_zero = f.read(512)
            # Ensure the read data is exactly 512 bytes in size
            if len(sector_zero) < 512:
                return False
        except OSError:
            logging.warning(f'No such device or address: {self.path}')
            return False
        else:
            return True
