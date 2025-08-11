# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""SCSI debug device management.

This module provides functionality for managing SCSI debug devices:
- Module loading/unloading
- Device discovery
- Failure injection

The SCSI debug driver (scsi_debug) creates virtual SCSI devices for testing:
- Simulates SCSI disk behavior
- Allows failure injection
- Supports multipath configurations
- Useful for testing without real hardware
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from sts.base import StorageDevice
from sts.multipath import MultipathDevice, MultipathService
from sts.utils.cmdline import run
from sts.utils.modules import ModuleInfo, ModuleManager


@dataclass
class ScsiDebugDevice(StorageDevice):
    """SCSI debug device.

    The scsi_debug module creates virtual SCSI devices that can:
    - Simulate various disk sizes and configurations
    - Inject failures on command
    - Test error handling and recovery
    - Verify multipath functionality

    Args:
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional, defaults to 'SCSI Debug')

    Example:
        ```python
        device = ScsiDebugDevice()  # Discovers first available device
        device = ScsiDebugDevice.create(size=1024 * 1024 * 1024)  # Creates new device
        ```
    """

    # Optional parameters from parent classes
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None

    # Internal fields
    module: ModuleManager = field(init=False, default_factory=ModuleManager)
    multipath: MultipathService = field(init=False, default_factory=MultipathService)

    # Sysfs path for module parameters
    SYSFS_PATH: ClassVar[Path] = Path('/sys/bus/pseudo/drivers/scsi_debug')

    def __post_init__(self) -> None:
        """Initialize device.

        Sets default model name if not provided.
        """
        # Set model if not provided
        if not self.model:
            self.model = 'SCSI Debug'

        # Initialize parent class
        super().__post_init__()

    @staticmethod
    def get_scsi_name_by_vendor(vendor: str) -> list[str] | None:
        """Get SCSI device names by vendor.

        Uses lsscsi to find devices with matching vendor string.
        For scsi_debug devices, vendor is typically 'Linux'.

        Args:
            vendor: Device vendor (e.g. 'Linux' for scsi_debug)

        Returns:
            List of device names (e.g. ['sda', 'sdb']) or None if not found
        """
        result = run('lsscsi -s')
        if result.failed:
            return None

        devices = []
        for line in result.stdout.splitlines():
            if vendor in line:
                # Parse line like: [0:0:0:0] disk Linux SCSI disk 1.0 /dev/sda 1024M
                parts = line.split()
                if len(parts) >= 6:
                    devices.append(parts[5].split('/')[-1])

        return devices or None

    @classmethod
    def create(cls, *, size: int | None = None, options: str | None = None) -> ScsiDebugDevice | None:
        """Create SCSI debug device.

        Creates a new virtual SCSI device by loading the scsi_debug module.
        Key module parameters:
        - dev_size_mb: Device size in megabytes
        - num_tgts: Number of targets (default: 1)
        - max_luns: Maximum LUNs per target (default: 1)

        Args:
            size: Device size in bytes (minimum 1MB)
            options: Additional module options (e.g. 'num_tgts=2 max_luns=4')

        Returns:
            ScsiDebugDevice instance or None if creation failed

        Example:
            ```python
            device = ScsiDebugDevice.create(size=1024 * 1024 * 1024)
            device.exists
            True
            ```
        """
        # Convert size to megabytes for module parameter
        if size:
            size_mb = size // (1024 * 1024)
            size_mb = max(size_mb, 1)  # Minimum 1MB
        else:
            size_mb = 8  # Default 8MB

        # Build module options
        module_options = f'dev_size_mb={size_mb}'
        if options:
            module_options = f'{module_options} {options}'

        # Load scsi_debug module with options
        module = ModuleManager()
        if not module.load('scsi_debug', module_options):
            return None

        # Get created device names
        devices = cls.get_devices()
        if not devices:
            return None

        # Return first device
        return cls(name=devices[0], size=size)

    def remove(self) -> bool:
        """Remove SCSI debug device.

        Cleanup process:
        1. Remove any multipath devices using this device
        2. Unload the scsi_debug module
        3. Device nodes are automatically removed

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device = ScsiDebugDevice.create(size=1024 * 1024 * 1024)
            device.remove()
            True
            ```
        """
        # Remove multipath devices if active
        if self.multipath.is_running():
            for _mpath in MultipathDevice.get_by_vendor('Linux'):
                if not self.multipath.flush():
                    return False
        # Unload scsi_debug module
        return self.module.unload('scsi_debug')

    def set_param(self, param_name: str, value: str | int) -> bool:
        """Set device parameter.

        Sets module parameters through sysfs:
        - Parameters control device behavior
        - Changes take effect immediately
        - Some parameters are read-only

        Args:
            param_name: Parameter name (e.g. 'every_nth', 'opts')
            value: Parameter value

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.set_param('every_nth', 1)
            True
            ```
        """
        param = self.SYSFS_PATH / param_name
        try:
            param.write_text(str(value))
        except OSError:
            logging.exception(f'Failed to set parameter: {param_name}={value}')
            return False

        return True

    def inject_failure(self, every_nth: int = 0, opts: int = 0) -> bool:
        """Inject device failures.

        Controls failure injection behavior:
        - every_nth: Frequency of failures
        - opts: Type and behavior of failures

        Args:
            every_nth: How often to inject failure (0 = disabled)
            opts: Failure options (bitmask):
                1 - "noisy": Log detailed error messages
                2 - "medium error": Report media errors
                4 - ignore "nth": Always inject failures
                8 - cause "nth" read/write to yield RECOVERED_ERROR
                16 - cause "nth" read/write to yield ABORTED_COMMAND

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Inject media errors on every operation
            device.inject_failure(every_nth=1, opts=2)
            True
            ```
        """
        if not self.set_param('every_nth', every_nth):
            return False
        return self.set_param('opts', opts)

    @classmethod
    def get_devices(cls) -> list[str] | None:
        """Get SCSI debug devices.

        Checks if scsi_debug module is loaded and returns all direct SCSI devices from scsi_debug.

        Returns:
            List of device names or None if no devices

        Example:
            ```python
            ScsiDebugDevice.get_devices()
            ['sda', 'sdb']
            ```
        """
        # Check if module is loaded
        if not ModuleInfo.from_name('scsi_debug'):
            return None

        # Fall back to direct SCSI devices
        return cls.get_scsi_name_by_vendor('Linux')
