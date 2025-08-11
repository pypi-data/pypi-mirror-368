# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Multipath device management.

This module provides functionality for managing multipath devices:
- Device discovery
- Path management
- Configuration management
- Service management

Device Mapper Multipath provides:
- I/O failover for redundancy
- I/O load balancing for performance
- Automatic path management
- Consistent device naming

Common use cases:
- High availability storage
- SAN connectivity
- iSCSI with multiple NICs
- FC with multiple HBAs
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Final, Literal

from sts.dm import DmDevice
from sts.utils.cmdline import run
from sts.utils.system import SystemManager

PACKAGE_NAME: Final[str] = 'device-mapper-multipath'


@dataclass
class MultipathDevice(DmDevice):
    """Multipath device representation.

    A multipath device combines multiple physical paths to the same storage
    into a single virtual device. This provides:
    - Automatic failover if paths fail
    - Load balancing across paths
    - Consistent device naming

    Args:
        name: Device name (optional, defaults to first available mpathX)
        path: Device path (optional, defaults to /dev/mapper/<name>)
        size: Device size in bytes (optional, discovered from device)
        dm_name: Device Mapper name (optional, discovered from device)
        model: Device model (optional)
        uuid: Device UUID (optional)
        wwid: Device WWID (optional, discovered from device)
        vendor: Device vendor (optional)
        n_paths: Number of paths
        size_str: Device size as a string (optional, discovered from device)
        features: Features of the device (optional, discovered from device)
        hwhandler: Hardware handler (optional, discovered from device)
        path_groups: List of path groups (optional, discovered from device)

    Example:
        ```python
        device = MultipathDevice()  # Uses first available device
        device = MultipathDevice(name='mpatha')  # Uses specific device
        device = MultipathDevice(name='360a98000324669436c2b45666c567867')
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    dm_name: str | None = None
    model: str | None = None
    uuid: str | None = None

    # Optional parameters for this class
    wwid: str | None = None  # World Wide ID (unique identifier)
    vendor: str | None = None  # Device vendor
    n_paths: int | None = None  # Number of paths

    # Additional optional parameters
    size_str: str | None = None  # Size as a string
    features: str | None = None  # Features of the device
    hwhandler: str | None = None  # Hardware handler
    path_groups: list[dict[str, Any]] = field(default_factory=list)  # Path groups

    # Configuration file paths
    MULTIPATH_CONF: ClassVar[Path] = Path('/etc/multipath.conf')
    MULTIPATH_BINDINGS: ClassVar[Path] = Path('/etc/multipath/bindings')

    def __post_init__(self) -> None:
        """Initialize multipath device.

        - Finds first available device if name not provided
        - Sets device path if not provided
        - Discovers device information and paths

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Get first available device if name not provided
        if not self.name:
            result = run('multipath -ll -v1')
            if result.succeeded and result.stdout:
                self.name = result.stdout.split()[0]

        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = Path(f'/dev/mapper/{self.name}')

        # Initialize parent class
        super().__post_init__()

        # Get device information if name provided
        if self.name:
            result = run(f'multipathd show map {self.name} json')
            if result.succeeded:
                dev_info = json.loads(result.stdout)['map']
                self._set_device_attributes(dev_info)

    def _set_device_attributes(self, dev_info: dict[str, Any]) -> None:
        """Set device attributes from dev_info dictionary.

        Args:
            dev_info: A dictionary containing device information.

        """
        # Log the start of attribute setting
        logging.debug(f'Setting attributes for device {self.name} from dev_info.')

        # Set attributes only if they exist in dev_info
        if 'uuid' in dev_info:
            self.uuid = dev_info['uuid']
            self.wwid = dev_info['uuid']
        if 'sysfs' in dev_info:
            self.dm_name = dev_info['sysfs']
        if 'failback' in dev_info:
            self.failback = dev_info['failback']
        if 'prod' in dev_info:
            self.model = dev_info['prod']
        if 'vend' in dev_info:
            self.vendor = dev_info['vend']
        if 'paths' in dev_info:
            self.n_paths = dev_info['paths']
        if 'dm_st' in dev_info:
            self.dm_st = dev_info['dm_st']
        if 'size_str' in dev_info:
            self.size_str = dev_info['size_str']
        if 'features' in dev_info:
            self.features = dev_info['features']
        if 'hwhandler' in dev_info:
            self.hwhandler = dev_info['hwhandler']
        if 'path_groups' in dev_info:
            self.path_groups = dev_info['path_groups']

        # Log the completion of attribute setting
        logging.debug(f'Attributes for device {self.name} set successfully.')

    def suspend(self) -> bool:
        """Suspend device.

        Temporarily disables the multipath device:
        - Stops using device for I/O
        - Keeps paths configured
        - Device can be resumed later

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.suspend()
            True
            ```
        """
        if not self.name:
            logging.error('Device name not available')
            return False

        result = run(f'multipath -f {self.name}')
        if result.failed:
            logging.error('Failed to suspend device')
            return False
        return True

    def resume(self) -> bool:
        """Resume device.

        Re-enables a suspended multipath device:
        - Rescans paths
        - Restores device operation
        - Resumes I/O handling

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.resume()
            True
            ```
        """
        if not self.name:
            logging.error('Device name not available')
            return False

        result = run(f'multipath -a {self.name}')
        if result.failed:
            logging.error('Failed to resume device')
            return False
        return True

    def remove(self) -> bool:
        """Remove device.

        Completely removes the multipath device:
        - Flushes I/O
        - Removes device mapper table
        - Clears path information

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.remove()
            True
            ```
        """
        if not self.name:
            logging.error('Device name not available')
            return False

        result = run(f'multipath -f {self.name}')
        if result.failed:
            logging.error('Failed to remove device')
            return False
        return True

    @property
    def paths(self) -> list[dict]:
        """Retrieves all path details for the device.

        Returns:
            A list of dictionaries containing detailed attributes for each path.

        """
        return [path for group in self.path_groups for path in group.get('paths', [])]

    @classmethod
    def get_all(cls) -> list[MultipathDevice]:
        """Retrieves all multipath devices available on the system.

        Returns:
            A list of `MultipathDevice` instances representing all detected multipath devices.
            If no devices are found or an error occurs, an empty list is returned.

        Examples:
            ```Python
            MultipathDevice.get_all()
            ```

        """
        result = run('multipath -ll -v1')
        if result.failed:
            logging.warning(f'Running "multipath -ll -v1" failed:\n{result.stderr}')
            return []

        return [cls(name=dev) for dev in result.stdout.splitlines() if dev.strip()]

    @classmethod
    def get_by_wwid(cls, wwid: str) -> MultipathDevice | None:
        """Get multipath device by WWID.

        The World Wide ID uniquely identifies a storage device:
        - Consistent across reboots
        - Same for all paths to device
        - Vendor-specific format

        Args:
            wwid: Device WWID

        Returns:
            MultipathDevice instance or None if not found

        Example:
            ```python
            MultipathDevice.get_by_wwid('360000000000000000e00000000000001')
            ```
        """
        if not wwid:
            msg = 'WWID required'
            raise ValueError(msg)

        for device in cls.get_all():
            if isinstance(device, MultipathDevice) and device.wwid == wwid:
                return device

        return None

    @classmethod
    def get_by_vendor(cls, vendor: str) -> list[MultipathDevice]:
        """Get multipath devices by vendor.

        Args:
            vendor: Device vendor (e.g. 'Linux')

        Returns:
            List of MultipathDevice instances or empty list if not found

        Example:
            ```python
            MultipathDevice.get_by_vendor('Linux')
            ```
        """
        if not vendor:
            msg = 'Vendor required'
            raise ValueError(msg)

        devices = cls.get_all()
        return [device for device in devices if device.vendor == vendor]


class MultipathService:
    """Multipath service management.

    Manages the multipathd service which:
    - Monitors path status
    - Handles path failures
    - Manages device creation
    - Applies configuration

    Example:
        ```python
        service = MultipathService()
        service.start()
        True
        ```
    """

    def __init__(self) -> None:
        """Initialize multipath service."""
        self.config_path = MultipathDevice.MULTIPATH_CONF
        # Ensure package is installed
        system = SystemManager()
        if not system.package_manager.install(PACKAGE_NAME):
            logging.critical(f'Could not install {PACKAGE_NAME}')

    def start(self) -> bool:
        """Start multipath service.

        Starts the multipathd daemon:
        - Creates default config if needed
        - Starts systemd service
        - Begins path monitoring

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.start()
            True
            ```
        """
        # Create default config if needed
        if not self.config_path.exists():
            result = run('mpathconf --enable')
            if result.failed:
                logging.error('Failed to create default config')
                return False

        result = run('systemctl start multipathd')
        if result.failed:
            logging.error('Failed to start multipathd')
            return False

        return True

    def stop(self) -> bool:
        """Stop multipath service.

        Stops the multipathd daemon:
        - Stops path monitoring
        - Keeps devices configured
        - Maintains configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.stop()
            True
            ```
        """
        result = run('systemctl stop multipathd')
        if result.failed:
            logging.error('Failed to stop multipathd')
            return False

        return True

    def reload(self) -> bool:
        """Reload multipath configuration.

        Reloads configuration without restart:
        - Applies config changes
        - Keeps devices active
        - Updates path settings

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.reload()
            True
            ```
        """
        result = run('systemctl reload multipathd')
        if result.failed:
            logging.error('Failed to reload multipathd')
            return False

        return True

    def is_running(self) -> bool:
        """Check if multipath service is running.

        Returns:
            True if running, False otherwise

        Example:
            ```python
            service.is_running()
            True
            ```
        """
        result = run('systemctl is-active multipathd')
        return result.succeeded

    def configure(
        self,
        find_multipaths: Literal['yes', 'no', 'strict', 'greedy', 'smart'] | None = None,
    ) -> bool:
        """Configure multipath service.

        Sets up multipath configuration:
        - find_multipaths modes:
          - yes: Create multipath devices for likely candidates
          - no: Only create explicitly configured devices
          - strict: Only create devices with multiple paths
          - greedy: Create devices for all SCSI devices
          - smart: Create devices based on WWID patterns

        Args:
            find_multipaths: How to detect multipath devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.configure(find_multipaths='yes')
            True
            ```
        """
        cmd = ['mpathconf', '--enable']
        if find_multipaths:
            cmd.extend(['--find_multipaths', find_multipaths])

        result = run(' '.join(cmd))
        if result.failed:
            logging.error('Failed to configure multipathd')
            return False

        return True

    def flush(self) -> bool:
        """Flush all unused multipath devices.

        Removes unused multipath devices:
        - Clears device mapper tables
        - Removes path groups
        - Keeps configuration intact

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            service.flush()
            True
            ```
        """
        result = run('multipath -F')
        if result.failed:
            logging.error('Failed to flush devices')
            return False

        return True
