# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""VDO device management.

This module provides functionality for managing VDO devices:
- VDO volume creation/removal
- Deduplication and compression
- Device statistics

VDO (Virtual Data Optimizer) is a kernel module that provides inline
data reduction through:
- Deduplication: Eliminates duplicate blocks
- Compression: Reduces block size using LZ4 algorithm
- Thin provisioning: Allocates space on demand
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import ClassVar, Literal, TypedDict

from sts.lvm import LogicalVolume
from sts.utils.cmdline import run

# Constants
DEFAULT_SLAB_SIZE = '2G'  # Default allocation unit size
MIN_SLAB_SIZE_MB = 128  # Minimum slab size (128 MB)
MAX_SLABS = 8192  # Maximum number of slabs per volume
DEFAULT_SLAB_SIZE_MB = 2048  # Default slab size in MB (2 GB)

# Size multipliers for parsing device sizes
SIZE_MULTIPLIERS = ['M', 'G', 'T', 'P', 'E']  # Mega, Giga, Tera, Peta, Exa

# Write policy options:
# - sync: Acknowledge writes after writing to physical storage
# - async: Acknowledge writes after writing to memory
WritePolicy = Literal['sync', 'async']


class VdoState(str, Enum):
    """VDO feature state.

    Used to enable/disable features like compression and deduplication.
    """

    ENABLED = 'y'
    DISABLED = 'n'


class VdoOptions(TypedDict, total=False):
    """VDO volume options.

    Common options:
    - size: Volume size (e.g. '1G', '500M')
    - extents: Volume size in LVM extents
    - type: Volume type (must be 'vdo')
    - compression: Enable compression (y/n)
    - deduplication: Enable deduplication (y/n)
    - vdowritepolicy: Write policy (sync/async)
    - vdoslabsize: Slab size - allocation unit (e.g. '2G', '512M')

    The slab size affects memory usage and performance:
    - Larger slabs = Better performance but more memory
    - Smaller slabs = Less memory but lower performance
    """

    size: str
    extents: str
    type: str
    compression: VdoState
    deduplication: VdoState
    vdowritepolicy: WritePolicy
    vdoslabsize: str


def get_minimum_slab_size(device: str | Path, *, use_default: bool = True) -> str:
    """Get minimum slab size for device.

    Calculates the minimum slab size based on device size:
    1. Get device size
    2. Calculate minimum size that allows MAX_SLABS
    3. Ensure size is at least MIN_SLAB_SIZE_MB
    4. Optionally use default if calculated size is smaller

    Args:
        device: Device path
        use_default: Return default size if calculated size is smaller

    Returns:
        Slab size string (e.g. '2G')

    Example:
        ```python
        get_minimum_slab_size('/dev/sda')
        '2G'
        get_minimum_slab_size('/dev/sdb', use_default=False)
        '512M'
        ```
    """
    device = Path(device)

    # Get device name - handle MD devices specially
    if str(device).startswith('/dev/md'):
        # For MD (RAID) devices, resolve the actual device name
        result = run(f'ls -al /dev/md | grep {device.name}')
        if result.failed:
            logging.warning(f'Device {device.name} not found in /dev/md')
            return DEFAULT_SLAB_SIZE
        device = Path(result.stdout.split('../')[-1])

    # Get device size from lsblk output
    result = run(f"lsblk | grep '{device.name} '")
    if result.failed:
        logging.warning(f'Device {device.name} not found using lsblk')
        return DEFAULT_SLAB_SIZE

    # Parse size (e.g. '1G', '2T') and convert to MB
    size = result.stdout.split()[3]
    multiplier = SIZE_MULTIPLIERS.index(size[-1:])
    device_size = int(float(size[:-1]) * (1024**multiplier))

    # Calculate minimum size:
    # 1. Divide device size by MAX_SLABS
    # 2. Round up to next power of 2
    # 3. Ensure at least MIN_SLAB_SIZE_MB
    minimum_size = 2 ** int(device_size / MAX_SLABS).bit_length()
    minimum_size = max(minimum_size, MIN_SLAB_SIZE_MB)

    # Use default size if calculated size is smaller
    if use_default and minimum_size < DEFAULT_SLAB_SIZE_MB:
        return DEFAULT_SLAB_SIZE
    return f'{minimum_size}M'


@dataclass
class VdoDevice(LogicalVolume):
    """VDO device.

    This class extends LogicalVolume to provide VDO-specific functionality:
    - Inline deduplication
    - Inline compression
    - Configurable write policy
    - Statistics reporting

    Args:
        name: Device name
        path: Device path
        size: Device size in bytes
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        vg: Volume group name
        deduplication: Enable deduplication
        compression: Enable compression
        write_policy: Write policy (sync/async)
        slab_size: Slab size (e.g. '2G', '512M')

    Example:
        ```python
        device = VdoDevice.create('vdo0', vg='vg0', size='1G')
        device.exists
        True
        ```
    """

    # VDO-specific options
    deduplication: bool = True
    compression: bool = True
    write_policy: WritePolicy = 'sync'
    slab_size: str | None = None

    # Class-level paths
    CONFIG_PATH: ClassVar[Path] = Path('/etc/vdoconf.yml')

    def create(self, **options: str) -> bool:
        """Create VDO volume.

        Creates a new VDO volume with specified options:
        - Compression and deduplication state
        - Write policy (sync/async)
        - Slab size for memory allocation

        Args:
            **options: VDO parameters (see VdoOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device = VdoDevice('vdo0', vg='vg0')
            device.create(size='1G')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group required')
            return False

        # Build VDO-specific options
        vdo_opts = [
            '--type',
            'vdo',
            '--compression',
            VdoState.ENABLED if self.compression else VdoState.DISABLED,
            '--deduplication',
            VdoState.ENABLED if self.deduplication else VdoState.DISABLED,
            '--vdowritepolicy',
            self.write_policy,
        ]
        if self.slab_size:
            vdo_opts.extend(['--vdoslabsize', self.slab_size])

        # Create VDO volume using LVM
        result = self._run('lvcreate', '-n', self.name, self.vg, *vdo_opts, **options)
        return result.succeeded

    def remove(self, **options: str) -> bool:
        """Remove VDO volume.

        Removes the VDO volume and its metadata.
        All data will be lost.

        Args:
            **options: VDO parameters (see VdoOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device = VdoDevice('vdo0', vg='vg0')
            device.remove()
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group required')
            return False

        result = self._run('lvremove', f'{self.vg}/{self.name}', **options)
        return result.succeeded

    def get_stats(self, *, human_readable: bool = True) -> dict[str, str] | None:
        """Get VDO statistics.

        Retrieves statistics about:
        - Space usage (physical vs logical)
        - Deduplication ratio
        - Compression ratio
        - Block allocation

        Args:
            human_readable: Use human readable sizes (e.g. '1.0G' vs bytes)

        Returns:
            Dictionary of statistics or None if error

        Example:
            ```python
            device = VdoDevice('vdo0', vg='vg0')
            stats = device.get_stats()
            stats['physical_blocks']  # Actually used space
            '1.0G'
            stats['data_blocks']  # Space before optimization
            '500M'
            ```
        """
        cmd = ['vdostats']
        if human_readable:
            cmd.append('--human-readable')
        cmd.append(str(self.path))

        result = run(' '.join(cmd))
        if result.failed:
            logging.error(f'Failed to get VDO stats: {result.stderr}')
            return None

        # Parse statistics output
        stats: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            stats[key.strip().lower().replace(' ', '_')] = value.strip()

        return stats

    def set_deduplication(self, *, enabled: bool = True) -> bool:
        """Set deduplication state.

        Enables or disables inline deduplication:
        - When enabled, duplicate blocks are detected and eliminated
        - When disabled, all blocks are stored as-is

        Args:
            enabled: Enable or disable deduplication

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device = VdoDevice('vdo0', vg='vg0')
            device.set_deduplication(enabled=False)
            True
            ```
        """
        cmd = 'enableDeduplication' if enabled else 'disableDeduplication'
        result = run(f'vdo {cmd} --name={self.name}')
        if result.failed:
            logging.error(f'Failed to set deduplication: {result.stderr}')
            return False

        self.deduplication = enabled
        return True

    def set_compression(self, *, enabled: bool = True) -> bool:
        """Set compression state.

        Enables or disables inline compression:
        - When enabled, blocks are compressed using LZ4
        - When disabled, blocks are stored uncompressed

        Args:
            enabled: Enable or disable compression

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device = VdoDevice('vdo0', vg='vg0')
            device.set_compression(enabled=False)
            True
            ```
        """
        cmd = 'enableCompression' if enabled else 'disableCompression'
        result = run(f'vdo {cmd} --name={self.name}')
        if result.failed:
            logging.error(f'Failed to set compression: {result.stderr}')
            return False

        self.compression = enabled
        return True

    def set_write_policy(self, policy: WritePolicy) -> bool:
        """Set write policy.

        Changes how writes are acknowledged:
        - sync: Wait for physical write (safer but slower)
        - async: Acknowledge after memory write (faster but risk data loss)

        Args:
            policy: Write policy (sync/async)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device = VdoDevice('vdo0', vg='vg0')
            device.set_write_policy('async')
            True
            ```
        """
        result = run(f'vdo changeWritePolicy --name={self.name} --writePolicy={policy}')
        if result.failed:
            logging.error(f'Failed to set write policy: {result.stderr}')
            return False

        self.write_policy = policy
        return True
