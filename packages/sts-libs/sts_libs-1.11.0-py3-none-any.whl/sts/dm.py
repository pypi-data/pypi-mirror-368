# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Device Mapper device management.

This module provides functionality for managing Device Mapper devices:
- Device discovery
- Device information
- Device operations
- Device Mapper targets

Device Mapper is a Linux kernel framework for mapping physical block devices
onto higher-level virtual block devices. It forms the foundation for (example):
- LVM (Logical Volume Management)
- Software RAID (dm-raid)
- Disk encryption (dm-crypt)
- Thin provisioning (dm-thin)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from sts.base import StorageDevice
from sts.utils.cmdline import run
from sts.utils.errors import DeviceError, DeviceNotFoundError

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class DmTarget:
    """Base class for Device Mapper targets.

    Device Mapper targets define how I/O operations are processed.
    Each target maps a range of the virtual device to one or more
    physical devices, optionally transforming the I/O in some way.

    Args:
        start: Start sector (where this target begins)
        size: Size in sectors (length of this target)
        args: Target-specific arguments (e.g. device paths, options)
    """

    start: int
    size: int
    args: str

    @property
    def type(self) -> str:
        """Get target type.

        Returns:
            Target type string (e.g. 'linear', 'thin-pool')
        """
        # Remove 'target' suffix from class name and convert to lowercase
        return self.__class__.__name__.lower().removesuffix('target')

    def __str__(self) -> str:
        """Return target table entry.

        Format: <start> <size> <type> <args>
        Used in dmsetup table commands.
        """
        return f'{self.start} {self.size} {self.type} {self.args}'


@dataclass
class LinearTarget(DmTarget):
    """Linear target.

    The simplest target type - maps a linear range of the virtual device
    directly onto a linear range of another device.

    Args format: <destination device> <sector offset>

    Example:
        ```python
        target = LinearTarget(0, 1000000, '253:0 0')  # Map to device 253:0 starting at sector 0
        str(target)
        '0 1000000 linear 253:0 0'
        ```
    """


@dataclass
class DelayTarget(DmTarget):
    """Delay target.

    Delays I/O operations by a specified amount. Useful for testing
    how applications handle slow devices.

    Args format: <device> <offset> <delay in milliseconds>

    Example:
        ```python
        target = DelayTarget(0, 1000000, '253:0 0 100')  # 100ms delay
        str(target)
        '0 1000000 delay 253:0 0 100'
        ```
    """


@dataclass
class MultipathTarget(DmTarget):
    """Multipath target.

    Provides I/O failover across multiple paths to the same device.
    Used for high availability storage configurations.

    Args format: <# of feature args> <# of paths> <features...> <path specs...>

    Example:
        ```python
        # Round-robin across two paths with queue_if_no_path
        target = MultipathTarget(0, 1000000, '2 1 round-robin 0 2 1 8:32 1000 8:48 1000')
        str(target)
        '0 1000000 multipath 2 1 round-robin 0 2 1 8:32 1000 8:48 1000'
        ```
    """


@dataclass
class ThinPoolTarget(DmTarget):
    """Thin pool target.

    Manages a pool of storage space from which thin volumes can be allocated.
    Enables thin provisioning - allocating more virtual space than physical.

    Args format: <metadata dev> <data dev> <block size> <low water mark> <flags> <args>

    Example:
        ```python
        # Pool with 128 sector blocks and 32768 low water mark
        target = ThinPoolTarget(0, 1000000, '253:0 253:1 128 32768 1 skip_block_zeroing')
        str(target)
        '0 1000000 thin-pool 253:0 253:1 128 32768 1 skip_block_zeroing'
        ```
    """


@dataclass
class ThinTarget(DmTarget):
    """Thin target.

    A virtual device that allocates space from a thin pool on demand.
    Enables over-provisioning of storage.

    Args format: <pool dev> <dev id>

    Example:
        ```python
        target = ThinTarget(0, 1000000, '253:0 1')  # Device 1 from pool 253:0
        str(target)
        '0 1000000 thin 253:0 1'
        ```
    """


@dataclass
class DmDevice(StorageDevice):
    """Device Mapper device representation.

    A Device Mapper device is a virtual block device that maps to one or
    more physical devices through a table of targets.

    Args:
        name: Device name (optional, e.g. 'dm-0')
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        dm_name: Device Mapper name (optional, discovered from device)
        model: Device model (optional)
        uuid: Device UUID (optional)

    Example:
        ```python
        device = DmDevice('dm-0')  # Create from kernel name
        device = DmDevice(dm_name='vg-lv')  # Create from mapper name
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None

    # Optional parameters for this class
    dm_name: str | None = None  # Mapper name (e.g. 'vg-lv')
    uuid: str | None = None  # Unique identifier

    # Internal fields
    _table: str | None = field(init=False, default=None)

    # Class-level paths
    DM_PATH: ClassVar[Path] = Path('/sys/class/block')  # Sysfs block devices
    DM_DEV_PATH: ClassVar[Path] = Path('/dev/mapper')  # Device nodes

    def __post_init__(self) -> None:
        """Initialize Device Mapper device.

        - Sets device path if not provided
        - Discovers mapper name if not provided
        - Loads device table

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        # Initialize parent class
        super().__post_init__()

        # Get device mapper name if not provided
        if not self.dm_name and self.name:
            result = run(f'dmsetup info -c --noheadings -o name {self.name}')
            if result.succeeded:
                self.dm_name = result.stdout.strip()

        # Get device table (defines how I/O is mapped)
        if self.dm_name:
            result = run(f'dmsetup table {self.dm_name}')
            if result.succeeded:
                self._table = result.stdout.strip()

    @property
    def device_path(self) -> Path:
        """Get path to device in sysfs.

        The sysfs path provides access to device attributes and statistics.

        Returns:
            Path to device directory

        Raises:
            DeviceNotFoundError: If device does not exist

        Example:
            ```python
            device.device_path
            PosixPath('/sys/class/block/dm-0')
            ```
        """
        if not self.name:
            msg = 'Device name not available'
            raise DeviceNotFoundError(msg)

        path = self.DM_PATH / self.name
        if not path.exists():
            msg = f'Device {self.name} not found'
            raise DeviceNotFoundError(msg)
        return path

    @property
    def table(self) -> str | None:
        """Get device table.

        The table defines how I/O requests are mapped to underlying devices.
        Format: <start sector> <length> <target type> <target args>

        Returns:
            Device table string or None if not available

        Example:
            ```python
            device.table
            '0 209715200 linear 253:0 0'
            ```
        """
        return self._table

    def suspend(self) -> bool:
        """Suspend device.

        Suspends I/O to the device. Required before changing the device table.
        Outstanding I/O will be queued until the device is resumed.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.suspend()
            True
            ```
        """
        if not self.dm_name:
            logging.error('Device mapper name not available')
            return False

        result = run(f'dmsetup suspend {self.dm_name}')
        if result.failed:
            logging.error('Failed to suspend device')
            return False
        return True

    def resume(self) -> bool:
        """Resume device.

        Resumes I/O to the device after suspension.
        Queued I/O will be processed.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.resume()
            True
            ```
        """
        if not self.dm_name:
            logging.error('Device mapper name not available')
            return False

        result = run(f'dmsetup resume {self.dm_name}')
        if result.failed:
            logging.error('Failed to resume device')
            return False
        return True

    def remove(self) -> bool:
        """Remove device.

        Removes the device mapping. The underlying devices are unaffected.
        Device must not be in use (mounted, etc).

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.remove()
            True
            ```
        """
        if not self.dm_name:
            logging.error('Device mapper name not available')
            return False

        result = run(f'dmsetup remove {self.dm_name}')
        if result.failed:
            logging.error('Failed to remove device')
            return False
        return True

    @classmethod
    def get_all(cls) -> Sequence[DmDevice]:
        """Get list of all Device Mapper devices.

        Lists all active device-mapper devices on the system.
        Currently only lists linear targets.

        Returns:
            List of DmDevice instances

        Example:
            ```python
            DmDevice.get_all()
            [DmDevice(name='dm-0', ...), DmDevice(name='dm-1', ...)]
            ```
        """
        devices = []
        # List only linear targets for now
        result = run('dmsetup ls --target linear')
        if result.failed:
            logging.warning('No Device Mapper devices found')
            return []

        for line in result.stdout.splitlines():
            try:
                # Parse line like: vg-lv (253:0)
                dm_name, dev_id = line.split()
                dev_id = dev_id.strip('()')
                major, minor = dev_id.split(':')

                # Get kernel device name (dm-N)
                result = run(f'ls -l /dev/dm-* | grep "{major}, *{minor}"')
                if result.failed:
                    continue
                name = result.stdout.split('/')[-1].strip()

                # Get device UUID for identification
                result = run(f'dmsetup info -c --noheadings -o uuid {dm_name}')
                uuid = result.stdout.strip() if result.succeeded else None

                devices.append(cls(name=name, dm_name=dm_name, uuid=uuid))
            except (ValueError, DeviceError):
                logging.exception('Failed to parse device info')
                continue

        return devices

    @classmethod
    def get_by_name(cls, dm_name: str) -> DmDevice | None:
        """Get Device Mapper device by name.

        Finds a device by its mapper name (e.g. 'vg-lv').
        More user-friendly than using kernel names (dm-N).

        Args:
            dm_name: Device Mapper name (e.g. 'vg-lv')

        Returns:
            DmDevice instance or None if not found

        Example:
            ```python
            DmDevice.get_by_name('vg-lv')
            DmDevice(name='dm-0', ...)
            ```
        """
        if not dm_name:
            msg = 'Device Mapper name required'
            raise ValueError(msg)

        for device in cls.get_all():
            if device.dm_name == dm_name:
                return device

        return None
