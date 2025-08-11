# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Loop device management.

This module provides functionality for managing loop devices:
- Device creation
- Device discovery
- Device operations
- Image file management

Loop devices allow regular files to be accessed as block devices.
Common uses include:
- Testing filesystem operations
- Mounting disk images
- Creating virtual block devices for testing
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar, Union

from sts.base import StorageDevice
from sts.utils.cmdline import run
from sts.utils.errors import DeviceError, DeviceNotFoundError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import TracebackType

# Constants
DEFAULT_SIZE_MB = 1024  # Default image file size
DEFAULT_IMAGE_SUFFIX = '.img'  # Default image file extension

# Type variables for generic class methods
T = TypeVar('T', bound='LoopDevice')

# Type aliases
LoopValue = Union[str, int, bool, None]  # Values from losetup output


@dataclass
class LoopDeviceInfo:
    """Loop device information from losetup -J.

    Parses and stores device information from losetup JSON output:
    - Device identification (name, backing file)
    - Device configuration (size limit, offset)
    - Device flags (autoclear, read-only, direct I/O)
    - Device parameters (sector size)

    Args:
        name: Device path (e.g. '/dev/loop0')
        back_file: Path to backing file (e.g. '/var/tmp/loop0.img')
        sizelimit: Size limit in bytes (0 = unlimited)
        offset: Offset in bytes (0 = start of file)
        autoclear: Whether device is automatically detached
        ro: Whether device is read-only
        dio: Whether direct I/O is enabled (bypass page cache)
        log_sec: Logical sector size in bytes
    """

    name: str
    back_file: str | None = None
    sizelimit: int | None = None
    offset: int | None = None
    autoclear: bool = False
    ro: bool = False
    dio: bool = False
    log_sec: int | None = None

    @staticmethod
    def _parse_bool(value: str | int | bool | None) -> bool:  # noqa: FBT001
        """Parse boolean value from losetup output.

        Handles various boolean representations:
        - Python bool (True/False)
        - Integer (0/1)
        - String ('true'/'false', '0'/'1', 'yes'/'no', 'on'/'off')

        Args:
            value: Value to parse (can be bool, int, str)

        Returns:
            Parsed boolean value
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return False

    @staticmethod
    def _parse_int(value: str | int | None) -> int | None:
        """Parse integer value from losetup output.

        Handles various integer representations:
        - Python int
        - String numeric value

        Args:
            value: Value to parse (can be int, str)

        Returns:
            Parsed integer value or None if invalid
        """
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoopDeviceInfo:
        """Create device info from dictionary.

        Parses losetup -J output format and converts values to appropriate types.

        Args:
            data: Dictionary from losetup -J output

        Returns:
            LoopDeviceInfo instance

        Example:
            ```python
            info = LoopDeviceInfo.from_dict(
                {
                    'name': '/dev/loop0',
                    'back-file': '/var/tmp/loop0.img',
                    'autoclear': '0',
                    'ro': False,
                }
            )
            info.name
            '/dev/loop0'
            info.autoclear
            False
            ```
        """
        # Required field
        if 'name' not in data:
            raise ValueError('Device name is required')

        # Parse optional fields with appropriate type conversion
        return cls(
            name=data['name'],
            back_file=data.get('back-file'),
            sizelimit=cls._parse_int(data.get('sizelimit')),
            offset=cls._parse_int(data.get('offset')),
            autoclear=cls._parse_bool(data.get('autoclear')),
            ro=cls._parse_bool(data.get('ro')),
            dio=cls._parse_bool(data.get('dio')),
            log_sec=cls._parse_int(data.get('log-sec')),
        )


@dataclass
class LoopDevice(StorageDevice):
    """Loop device representation.

    A loop device allows a regular file to be accessed as a block device.
    This enables testing of block device operations without real hardware.

    Key features:
    - Create devices with specified size
    - Attach/detach backing files
    - Query device status and configuration
    - Automatic cleanup via context manager

    Args:
        name: Device name (optional, e.g. 'loop0')
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        image_path: Path to backing image file (optional, discovered from device)

    Example:
        ```python
        device = LoopDevice(name='loop0')  # Discovers other values
        device = LoopDevice.create(size_mb=1024)  # Creates new device
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None

    # Optional parameters for this class
    image_path: Path | None = None

    # Internal fields
    _image_exists: bool = field(init=False, default=False)
    _info: LoopDeviceInfo | None = field(init=False, default=None)

    # Class-level paths
    LOOP_PATH: ClassVar[Path] = Path('/dev')  # Device nodes
    DEFAULT_IMAGE_PATH: ClassVar[Path] = Path('/var/tmp')  # Default image location

    def __post_init__(self) -> None:
        """Initialize loop device.

        - Sets device path if not provided
        - Gets device information from losetup
        - Checks backing file existence
        - Gets device size if not provided

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        # Initialize parent class
        super().__post_init__()

        # Get device info and backing file path
        if self.path:
            self._info = self._get_device_info()
            if self._info and self._info.back_file:
                self.image_path = Path(self._info.back_file)

        # Check if backing file exists
        if self.image_path and self.image_path.exists():
            self._image_exists = True

        # Get size from blockdev if not provided
        if not self.size and self.path:
            result = run(f'blockdev --getsize64 {self.path}')
            if result.succeeded:
                self.size = int(result.stdout)

    def _get_device_info(self) -> LoopDeviceInfo | None:
        """Get device information using losetup -J.

        Uses JSON output format for reliable parsing.

        Returns:
            LoopDeviceInfo instance or None if not found
        """
        result = run(f'losetup -lJ {self.path}')
        if result.failed or not result.stdout:
            return None

        try:
            data = json.loads(result.stdout)
            devices = data.get('loopdevices', [])
            if not devices:
                return None
            return LoopDeviceInfo.from_dict(devices[0])
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    def __enter__(self: T) -> T:
        """Enter context manager.

        Enables use of 'with' statement for automatic cleanup.

        Returns:
            Self for use in with statement

        Example:
            ```python
            with device:
                assert device.exists
            ```
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager.

        Automatically removes device and backing file when exiting context.

        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value if error occurred
            exc_tb: Exception traceback if error occurred

        Example:
            ```python
            with device:
                assert device.exists
            assert not device.exists
            ```
        """
        self.remove()

    @property
    def device_path(self) -> Path:
        """Get path to device.

        Returns:
            Path to device node (e.g. /dev/loop0)

        Raises:
            DeviceNotFoundError: If device does not exist

        Example:
            ```python
            device.device_path
            PosixPath('/dev/loop0')
            ```
        """
        if not self.name:
            msg = 'Device name not available'
            raise DeviceNotFoundError(msg)

        path = self.LOOP_PATH / self.name
        if not path.exists():
            msg = f'Device {self.name} not found'
            raise DeviceNotFoundError(msg)
        return path

    @property
    def backing_file(self) -> Path | None:
        """Get path to backing file.

        Returns:
            Path to backing file or None if not found

        Example:
            ```python
            device.backing_file
            PosixPath('/var/tmp/loop0.img')
            ```
        """
        if not self.path:
            return None

        info = self._get_device_info()
        if not info or not info.back_file:
            return None

        path = Path(info.back_file)
        return path if path.exists() else None

    def detach(self) -> bool:
        """Detach device from backing file.

        Removes the association between the loop device and its backing file.
        The backing file is not deleted.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.detach()
            True
            ```
        """
        if not self.path:
            logging.error('Device path not available')
            return False

        result = run(f'losetup -d {self.path}')
        if result.failed:
            logging.error('Failed to detach device')
            return False
        return True

    def remove(self) -> bool:
        """Remove device and backing file.

        Performs complete cleanup:
        1. Detaches device from backing file
        2. Removes backing file if it exists

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.remove()
            True
            ```
        """
        # Save image path before detaching
        image_path = self.image_path

        # Detach device
        if not self.detach():
            return False

        # Remove backing file if we have a valid path
        if image_path and image_path.exists() and image_path.is_file():
            try:
                image_path.unlink()
            except OSError:
                logging.exception('Failed to remove backing file')
                return False

        return True

    @classmethod
    def _prepare_image_file(
        cls,
        name: str,
        image_path: Path,
        size_mb: int,
        *,
        reuse_file: bool = False,
    ) -> Path | None:
        """Prepare image file for loop device.

        Creates or reuses a sparse file for the loop device:
        1. Handles existing file (remove or reuse)
        2. Creates parent directory if needed
        3. Creates sparse file of specified size

        Args:
            name: Device name
            image_path: Path to store image file
            size_mb: Size in megabytes
            reuse_file: Whether to reuse existing file

        Returns:
            Path to image file or None if preparation failed
        """
        image_file = image_path / f'{name}{DEFAULT_IMAGE_SUFFIX}'

        # Handle existing file
        if image_file.exists():
            if not reuse_file:
                try:
                    image_file.unlink()
                except OSError:
                    logging.exception('Failed to remove existing file')
                    return None
            return image_file

        # Create parent directory
        try:
            image_path.mkdir(parents=True, exist_ok=True)
        except OSError:
            logging.exception('Failed to create image directory')
            return None

        # Create sparse file (allocates blocks only when written)
        result = run(f'fallocate -l {size_mb}M {image_file}')
        if result.failed:
            logging.error('Failed to create image file')
            return None

        return image_file

    @classmethod
    def _attach_device(cls, name: str, image_file: Path) -> bool:
        """Attach loop device to image file.

        Associates a loop device with a backing file.

        Args:
            name: Device name
            image_file: Path to image file

        Returns:
            True if successful, False otherwise
        """
        result = run(f'losetup /dev/{name} {image_file}')
        if result.failed:
            logging.error('Failed to attach device')
            try:
                image_file.unlink()
            except OSError:
                logging.exception('Failed to clean up image file')
            return False
        return True

    @classmethod
    def create(
        cls: type[T],
        name: str | None = None,
        *,
        size_mb: int = DEFAULT_SIZE_MB,
        image_path: str | Path = DEFAULT_IMAGE_PATH,
        reuse_file: bool = False,
    ) -> T | None:
        """Create loop device.

        Creates a new loop device with specified parameters:
        1. Finds available device if name not provided
        2. Creates backing file
        3. Attaches device to file

        Args:
            name: Device name (optional, auto-detected if not provided)
            size_mb: Size in megabytes (default: 1024)
            image_path: Path to store image file (default: /var/tmp)
            reuse_file: Whether to reuse existing file (default: False)

        Returns:
            LoopDevice instance or None if creation failed

        Example:
            ```python
            device = LoopDevice.create(size_mb=1024)
            device.exists
            True
            ```
        """
        # Get next available device if name not provided
        if not name:
            result = run('losetup -f')
            if result.failed:
                logging.error('Failed to find free device')
                return None
            name = Path(result.stdout.strip()).name

        # Ensure name is standardized (remove /dev/ prefix)
        device_name = name.replace('/dev/', '')

        # Create image file
        image_file = cls._prepare_image_file(
            device_name,
            Path(image_path),
            size_mb,
            reuse_file=reuse_file,
        )
        if not image_file:
            return None

        # Attach device
        if not cls._attach_device(device_name, image_file):
            return None

        return cls(name=device_name, image_path=image_file)

    @classmethod
    def using(
        cls: type[T],
        name: str | None = None,
        *,
        size_mb: int = DEFAULT_SIZE_MB,
        image_path: str | Path = DEFAULT_IMAGE_PATH,
        reuse_file: bool = False,
    ) -> T:
        """Create loop device for use in context manager.

        Convenience method for creating a device in a 'with' statement.
        Ensures proper cleanup when the context exits.

        Args:
            name: Device name (optional, auto-detected if not provided)
            size_mb: Size in megabytes (default: 1024)
            image_path: Path to store image file (default: /var/tmp)
            reuse_file: Whether to reuse existing file (default: False)

        Returns:
            LoopDevice instance for use in with statement

        Example:
            ```python
            with LoopDevice.using(size_mb=1024) as device:
                assert device.exists
            ```
        """
        device = cls.create(
            name,
            size_mb=size_mb,
            image_path=image_path,
            reuse_file=reuse_file,
        )
        if not device:
            msg = 'Failed to create loop device'
            raise DeviceError(msg)
        return device

    @classmethod
    def get_all(cls: type[T]) -> Sequence[T]:
        """Get list of all loop devices.

        Uses losetup -J to get JSON output of all devices.

        Returns:
            List of LoopDevice instances

        Example:
            ```python
            LoopDevice.get_all()
            [LoopDevice(name='loop0', ...), LoopDevice(name='loop1', ...)]
            ```
        """
        result = run('losetup -lJ')
        if result.failed:
            logging.warning('No loop devices found')
            return []

        try:
            data = json.loads(result.stdout)
            devices = data.get('loopdevices', [])
            return [cls(name=Path(dev['name']).name) for dev in devices]
        except (json.JSONDecodeError, KeyError):
            logging.warning('Failed to parse loop devices')
            return []

    @classmethod
    def get_by_name(cls: type[T], name: str) -> T | None:
        """Get loop device by name.

        Args:
            name: Device name (e.g. 'loop0')

        Returns:
            LoopDevice instance or None if not found

        Example:
            ```python
            LoopDevice.get_by_name('loop0')
            LoopDevice(name='loop0', ...)
            ```
        """
        if not name:
            msg = 'Device name required'
            raise ValueError(msg)

        # Ensure name is standardized (remove /dev/ prefix)
        name = name.replace('/dev/', '')

        for device in cls.get_all():
            if device.name == name:
                return device

        return None
