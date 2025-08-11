# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Block device management module.

This module provides functionality for managing block devices:
- Device discovery
- Device information
- Device operations
"""

from __future__ import annotations

import json
import logging
from contextlib import suppress
from dataclasses import dataclass, field
from os import getenv
from pathlib import Path
from typing import Any, ClassVar

from sts.base import StorageDevice
from sts.lvm import PhysicalVolume
from sts.utils.cmdline import run
from sts.utils.errors import DeviceError

# Constants
MIN_BLOCKDEV_LINES = 2  # Minimum lines in blockdev output (header + data)


def _load_all_devices() -> list[dict[str, Any]]:
    """Load data for all block devices.

    Uses lsblk to get detailed information about all block devices in JSON format.
    This includes disks, partitions, LVM volumes, etc.

    Returns:
        List of device data dictionaries
    """
    # -J: JSON output
    # -O: All columns
    # -b: Bytes for sizes
    result = run('lsblk -JOb')
    if result.failed:
        logging.warning('Failed to get block devices')
        return []

    try:
        return json.loads(result.stdout)['blockdevices']
    except (json.JSONDecodeError, KeyError) as e:
        logging.warning(f'Failed to parse block devices: {e}')
        return []


def _process_device_data(data: dict[str, Any]) -> list[BlockDevice]:
    """Process device data from lsblk.

    Recursively processes device data to handle parent-child relationships
    (e.g., disk and its partitions).

    Args:
        data: Device data from lsblk

    Returns:
        List of BlockDevice instances
    """
    devices = []

    # Add start sector if missing (important for partition detection)
    if 'start' not in data:
        data['start'] = 0

    # Create device instance with cached data to avoid duplicate queries
    devices.append(BlockDevice(Path('/dev') / data['name'], _data_cache=data))

    # Recursively process child devices (partitions, etc.)
    if 'children' in data:
        for child in data['children']:
            devices.extend(_process_device_data(child))

    return devices


def get_all() -> list[BlockDevice]:
    """Get list of all block devices.

    Returns:
        List of BlockDevice instances

    Example:
        ```python
        get_all()
        [BlockDevice(path='/dev/sda'), BlockDevice(path='/dev/sda1')]
        ```
    """
    devices = []
    for data in _load_all_devices():
        devices.extend(_process_device_data(data))
    return devices


def get_free_disks() -> list[BlockDevice]:
    """Get list of unused block devices.

    A device is considered free if it:
    - Has no parent device (not a partition)
    - Has no child devices (no partitions)
    - Is not a LVM physical volume
    - Is not mounted
    - Is not READ-ONLY

    This is useful for finding disks that can be safely used for testing.

    Returns:
        List of BlockDevice instances

    Example:
        ```python
        get_free_disks()
        [BlockDevice(path='/dev/sdc')]
        ```
    """
    free_devices = []
    # Get list of LVM PVs to exclude
    pvs = PhysicalVolume.get_all().keys()

    for data in _load_all_devices():
        # Skip if device has parent (is partition) or children (has partitions)
        if data.get('pkname') or data.get('children'):
            continue

        # Skip if device is LVM PV
        if f'/dev/{data["name"]}' in pvs:
            continue

        # Skip if device is mounted
        if data.get('is_mounted'):
            continue

        # Skip if device is READ-ONLY
        if data.get('ro'):
            logging.debug(f'Device {data["name"]} is READ-ONLY.')
            continue

        # Add start sector if missing (needed for partition detection)
        if 'start' not in data:
            data['start'] = 0

        _block_device = BlockDevice(Path('/dev') / data['name'], _data_cache=data)

        # Double check mount status (belt and suspenders)
        if not _block_device.is_mounted:
            free_devices.append(_block_device)

    return free_devices


def filter_devices_by_block_sizes(
    block_devices: list[BlockDevice], *, prefer_matching_block_sizes: bool, required_devices: int = 0
) -> tuple[tuple[int, int], list[BlockDevice]]:
    """Filter block devices based on their block sizes, preferring devices with matching sector and block sizes.

    Args:
        block_devices: List of BlockDevice objects to filter
        required_devices: Minimum number of devices required (defaults to env var MIN_DEVICES or 0)
        prefer_matching_block_sizes: If True, prefer devices where sector_size matches block_size

    Returns:
        Tuple containing:
        - Tuple of (sector_size, block_size) for the chosen devices
        - List of device paths that match the criteria

    Example:
        >>> devices = [
        ...     BlockDevice('/dev/sda', sector_size=512, block_size=512),
        ...     BlockDevice('/dev/sdb', sector_size=512, block_size=4096),
        ...     BlockDevice('/dev/sdc', sector_size=512, block_size=512),
        ... ]
        >>> sizes, matching_devices = filter_devices_by_block_sizes(
        ...     devices, prefer_matching_block_sizes=True, required_devices=2
        ... )
        >>> sizes
        (512, 512)
        >>> [device.path for device in matching_devices]
        ['/dev/sda', '/dev/sdc']
    """
    if required_devices == 0:
        required_devices = int(getenv('MIN_DEVICES', '0'))

    if not block_devices:
        logging.warning('No block devices provided')
        return (0, 0), []

    # Group devices by their block sizes
    devices_by_block_sizes: dict[tuple[int, int], list[BlockDevice]] = {}
    for disk in block_devices:
        block_sizes = (disk.sector_size, disk.block_size)
        if block_sizes in devices_by_block_sizes:
            devices_by_block_sizes[block_sizes].append(disk)
        else:
            devices_by_block_sizes[block_sizes] = [disk]

    # Find the best group of devices based on preferences
    best_group_size = (0, 0)
    best_group_devices = []
    max_devices = 0

    for block_size, devices in devices_by_block_sizes.items():
        num_devices = len(devices)

        # Skip if we don't have enough devices and block sizes don't match
        if num_devices < required_devices and prefer_matching_block_sizes and block_size[0] != block_size[1]:
            continue

        # If we prefer matching block sizes and found a matching group with enough devices
        if prefer_matching_block_sizes and block_size[0] == block_size[1] and num_devices >= required_devices:
            best_group_size = block_size
            best_group_devices = devices
            break

        # Update best group if we found more devices
        if num_devices > max_devices:
            max_devices = num_devices
            best_group_size = block_size
            best_group_devices = devices

    logging.info(
        f'Using following disks: {", ".join([str(dev.path) for dev in best_group_devices])} '
        f'with block sizes: {best_group_size}'
    )

    return best_group_size, best_group_devices


@dataclass
class BlockDevice(StorageDevice):
    """Block device representation.

    This class extends StorageDevice with additional functionality:
    - Device information (size, model, type)
    - Device operations (read/write status)
    - Device state (mounted, removable)

    Args:
        path: Device path (e.g. '/dev/sda')
        _data_cache: Optional cached device data from lsblk

    Raises:
        DeviceError: If device is not a block device or cannot be queried
    """

    # Internal data caches to avoid repeated system calls
    _data_cache: dict[str, Any] | None = field(default=None, init=True, repr=False)
    _blockdev_data: dict[str, Any] = field(init=False, repr=False)
    _lsblk_data: dict[str, Any] = field(init=False, repr=False)

    # Sysfs path for block devices
    SYS_BLOCK_PATH: ClassVar[Path] = Path('/sys/dev/block')

    def __post_init__(self) -> None:
        """Initialize device data."""
        # Initialize parent class first
        super().__post_init__()

        # Load device data from cache or system
        if self._data_cache:
            self._blockdev_data = self._data_cache
            self._lsblk_data = self._data_cache
        else:
            # Query device data if not cached
            self._blockdev_data = self._load_blockdev_data()
            self._lsblk_data = self._load_lsblk_data()

        # Set common attributes from data
        self.size = self._blockdev_data['size']
        self.model = self._lsblk_data.get('model')

    def _load_blockdev_data(self) -> dict[str, Any]:
        """Load blockdev data for device.

        Uses blockdev --report to get low-level block device information
        like sector size, read-only status, etc.

        Returns:
            Dictionary of blockdev data

        Raises:
            DeviceError: If blockdev data cannot be loaded
        """
        result = run(f'blockdev --report {self.path}')
        if result.failed:
            raise DeviceError(f'Failed to get blockdev data: {result.stderr}')

        try:
            lines = result.stdout.splitlines()
            if len(lines) < MIN_BLOCKDEV_LINES:
                raise DeviceError(f'No data from {self.path}')

            # Parse blockdev output format:
            # RO RA SSZ BSZ StartSec Size Device
            header = lines[0].split()
            fields = lines[1].split()

            if header != ['RO', 'RA', 'SSZ', 'BSZ', 'StartSec', 'Size', 'Device']:
                raise DeviceError(f'Unknown output of blockdev: {header}')

            return {
                'ro': fields[0] != 'rw',
                'ra': int(fields[1]),
                'log-sec': int(fields[2]),
                'phy-sec': int(fields[3]),
                'start': int(fields[4]),
                'size': int(fields[5]),
            }
        except (IndexError, ValueError) as e:
            raise DeviceError(f'Invalid blockdev data: {e}') from e

    def _load_lsblk_data(self) -> dict[str, Any]:
        """Load lsblk data for device.

        Uses lsblk to get detailed device information like filesystem type,
        mount status, etc.

        Returns:
            Dictionary of lsblk data

        Raises:
            DeviceError: If lsblk data cannot be loaded
        """
        result = run(f'lsblk -JOb {self.path}')
        if result.failed:
            raise DeviceError(f'Failed to get lsblk data: {result.stderr}')

        try:
            blockdevs = json.loads(result.stdout)['blockdevices']
            if not blockdevs:
                raise DeviceError(f'No data from {self.path}')

            data = blockdevs[0]
            # Add start sector if missing (needed for partition detection)
            if 'start' not in data:
                data['start'] = self._get_start_sector(data)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise DeviceError(f'Invalid lsblk data: {e}') from e

        return data

    def _get_start_sector(self, data: dict[str, Any]) -> int:
        """Get start sector for device.

        For partitions, reads the start sector from sysfs.
        For whole disks, returns 0.

        Args:
            data: Device data from lsblk

        Returns:
            Start sector number (0 if not found)
        """
        if not data.get('pkname'):  # No parent device = whole disk
            return 0

        # Try reading start sector from sysfs
        with suppress(ValueError, DeviceError):
            result = run(f'cat {self.SYS_BLOCK_PATH}/{data["maj:min"]}/start')
            if result.succeeded and result.stdout:
                return int(result.stdout)

        return 0

    # Properties

    @property
    def is_partition(self) -> bool:
        """Return True if the device is a partition.

        Determined by start sector - partitions start after sector 0.

        Example:
            ```python
            BlockDevice('/dev/sda1').is_partition
            True
            BlockDevice('/dev/sda').is_partition
            False
            ```
        """
        return self._blockdev_data['start'] > 0

    @property
    def sector_size(self) -> int:
        """Return sector size for the device in bytes.

        Example:
            ```python
            BlockDevice('/dev/sda1').sector_size
            512
            ```
        """
        try:
            return self._blockdev_data['log-sec']
        except KeyError:
            return 0

    @property
    def block_size(self) -> int:
        """Return block size for the device in bytes.

        Example:
            ```python
            BlockDevice('/dev/sda').block_size
            4096
            ```
        """
        try:
            return self._blockdev_data['phy-sec']
        except KeyError:
            return 0

    @property
    def start_sector(self) -> int:
        """Return start sector of the device on the underlying device.

        Usually zero for full devices and non-zero for partitions.

        Example:
            ```python
            BlockDevice('/dev/sda1').start_sector
            2048
            BlockDevice('/dev/md0').start_sector
            0
            ```
        """
        return self._blockdev_data['start']

    @property
    def is_writable(self) -> bool:
        """Return True if device is writable (no RO status).

        Example:
            ```python
            BlockDevice('/dev/sda').is_writable
            True
            BlockDevice('/dev/loop1').is_writable
            False
            ```
        """
        return not self._blockdev_data['ro']

    @property
    def ra(self) -> int:
        """Return Read Ahead for the device in 512-bytes sectors.

        Read-ahead improves sequential read performance by pre-fetching data.

        Example:
            ```python
            BlockDevice('/dev/sda').ra
            256
            ```
        """
        return self._blockdev_data['ra']

    @property
    def is_removable(self) -> bool:
        """Return True if device is removable.

        Example:
            ```python
            BlockDevice('/dev/sda').is_removable
            False
            ```
        """
        return bool(self._lsblk_data['rm'])

    @property
    def hctl(self) -> str | None:
        """Return Host:Channel:Target:Lun for SCSI devices.

        SCSI addressing format used by the kernel.
        Not available for non-SCSI devices like NVMe.

        Example:
            ```python
            BlockDevice('/dev/sda').hctl
            '1:0:0:0'
            BlockDevice('/dev/nvme1n1').hctl
            None
            ```
        """
        return self._lsblk_data.get('hctl')

    @property
    def state(self) -> str | None:
        """Return state of the device.

        Example:
            ```python
            BlockDevice('/dev/nvme1n1').state
            'live'
            BlockDevice('/dev/nvme1n1p1').state
            None
            ```
        """
        return self._lsblk_data.get('state')

    @property
    def partition_type(self) -> str | None:
        """Return partition table type.

        Example:
            ```python
            BlockDevice('/dev/nvme1n1p1').partition_type
            'gpt'
            BlockDevice('/dev/nvme1n1').partition_type
            None
            ```
        """
        return self._lsblk_data.get('pttype')

    @property
    def wwn(self) -> str | None:
        """Return unique storage identifier.

        World Wide Name (WWN) uniquely identifies storage devices.
        Useful for tracking devices across reboots/reconnects.

        Example:
            ```python
            BlockDevice('/dev/nvme1n1').wwn
            'eui.00253856a5ebaa6f'
            BlockDevice('/dev/nvme1n1p1').wwn
            'eui.00253856a5ebaa6f'
            ```
        """
        return self._lsblk_data.get('wwn')

    @property
    def filesystem_type(self) -> str | None:
        """Return filesystem type.

        Example:
            ```python
            BlockDevice('/dev/nvme1n1p1').filesystem_type
            'vfat'
            BlockDevice('/dev/nvme1n1').filesystem_type
            None
            ```
        """
        return self._lsblk_data.get('fstype')

    @property
    def is_mounted(self) -> bool:
        """Return True if the device is mounted.

        Example:
            ```python
            BlockDevice('/dev/nvme1n1p1').is_mounted
            True
            ```
        """
        return bool(self._lsblk_data.get('mountpoint'))

    @property
    def type(self) -> str:
        """Return device type.

        Common types:
        - disk: Whole disk device
        - part: Partition
        - lvm: Logical volume
        - crypt: Encrypted device
        - mpath: Multipath device

        Example:
            ```python
            BlockDevice('/dev/nvme1n1').type
            'disk'
            BlockDevice('/dev/nvme1n1p1').type
            'part'
            BlockDevice('/dev/mapper/vg-lvol0').type
            'lvm'
            ```
        """
        return self._lsblk_data['type']

    @property
    def transport_type(self) -> str | None:
        """Return device transport type.

        Common types:
        - nvme: NVMe device
        - iscsi: iSCSI device
        - fc: Fibre Channel device

        Example:
            ```python
            BlockDevice('/dev/nvme1n1p1').transport_type
            'nvme'
            BlockDevice('/dev/sdc').transport_type
            'iscsi'
            ```
        """
        return self._lsblk_data.get('tran')

    def __repr__(self) -> str:
        """Return string representation of device."""
        return f'BlockDevice(path={self.path!r})'
