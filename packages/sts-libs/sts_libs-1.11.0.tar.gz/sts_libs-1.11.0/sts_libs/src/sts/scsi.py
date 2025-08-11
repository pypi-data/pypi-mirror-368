# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""SCSI device management.

This module provides functionality for managing SCSI devices:
- Device discovery
- Device information
- Device operations

SCSI (Small Computer System Interface) is a standard for:
- Storage device communication
- Device addressing and identification
- Command and data transfer
- Error handling and recovery

Common SCSI devices include:
- Hard drives (HDDs)
- Solid State Drives (SSDs)
- Tape drives
- CD/DVD/Blu-ray drives
"""

from __future__ import annotations

import contextlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, TypeVar

from sts.base import StorageDevice
from sts.utils.cmdline import run
from sts.utils.packages import ensure_installed

T = TypeVar('T', bound='ScsiDevice')


@dataclass
class ScsiDevice(StorageDevice):
    """SCSI device representation.

    A SCSI device is identified by:
    - SCSI ID (H:C:T:L format)
      - H: Host adapter number
      - C: Channel/Bus number
      - T: Target ID
      - L: Logical Unit Number (LUN)
    - Device node (e.g. /dev/sda)
    - Vendor and model information

    Args:
        name: Device name (optional, e.g. 'sda')
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        scsi_id: SCSI ID (optional, discovered from device)
        host_id: FC host ID (optional, discovered from device)

    Example:
        ```python
        device = ScsiDevice(name='sda')  # Discovers other values
        device = ScsiDevice(scsi_id='0:0:0:0')  # Discovers device from SCSI ID
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None

    # Optional parameters for this class
    scsi_id: str | None = None  # SCSI address (H:C:T:L)
    host_id: str | None = None

    # Sysfs path for SCSI devices
    SCSI_PATH: ClassVar[Path] = Path('/sys/class/scsi_device')
    SCSI_HOST_PATH: ClassVar[Path] = Path('/sys/class/scsi_host')

    def __post_init__(self) -> None:
        """Initialize SCSI device.

        - Sets device path if not provided
        - Gets device information from lsscsi
        - Gets model information if not provided

        Raises:
            DeviceNotFoundError: If device does not exist
            DeviceError: If device cannot be accessed
        """
        # Ensure lsscsi is installed
        ensure_installed('lsscsi')

        # Initialize parent class
        super().__post_init__()

        # Get SCSI ID from lsscsi if not provided
        if not self.scsi_id and self.name:
            result = run(f'lsscsi | grep "{self.name} $"')
            if result.succeeded:
                with contextlib.suppress(IndexError):
                    # Extract [H:C:T:L] from lsscsi output
                    self.scsi_id = result.stdout.split()[0].strip('[]')

        if self.scsi_id:
            self.host_id = self.scsi_id.strip('[]').split(':')[0]

        if self.scsi_id and not self.name:
            self.name = self.device_name

        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        # Get model from sysfs if not provided
        if not self.model:
            self.model = self.model_name

    @property
    def vendor(self) -> str | None:
        """Get device vendor.

        Reads vendor string from sysfs:
        - Common vendors: ATA, SCSI, USB
        - Helps identify device type and capabilities
        - Used for device-specific handling

        Returns:
            Device vendor or None if not available

        Example:
            ```python
            device.vendor
            'ATA'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            vendor_path = self.SCSI_PATH / self.scsi_id / 'device/vendor'
            return vendor_path.read_text().strip()
        except OSError:
            return None

    @property
    def model_name(self) -> str | None:
        """Get device model name.

        Reads model string from sysfs:
        - Identifies specific device model
        - Contains manufacturer information
        - Used for device compatibility

        Returns:
            Device model name or None if not available

        Example:
            ```python
            device.model_name
            'Samsung SSD 970 EVO'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            model_path = self.SCSI_PATH / self.scsi_id / 'device/model'
            return model_path.read_text().strip()
        except OSError:
            return None

    @property
    def revision(self) -> str | None:
        """Get device revision.

        Reads firmware revision from sysfs:
        - Indicates firmware version
        - Important for bug tracking
        - Used for feature compatibility

        Returns:
            Device revision or None if not available

        Example:
            ```python
            device.revision
            '1.0'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            rev_path = self.SCSI_PATH / self.scsi_id / 'device/rev'
            return rev_path.read_text().strip()
        except OSError:
            return None

    @property
    def device_name(self) -> str | None:
        """Get device name.

        Returns:
            Device name or None if not available

        Example:
            ```python
            device.device_name
            'sdc'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            block_path = Path(f'{self.SCSI_PATH}/{self.scsi_id}/device/block')
            if block_path.exists():
                return next(block_path.iterdir()).name
        except OSError:
            logging.warning(f'Failed to get the device name for {self.scsi_id}')
            return None
        else:
            return None

    @property
    def transport(self) -> str | None:
        """Get device transport.

        Returns:
            Device transport or None if not available

        Examples:
            ```Python
            device.transport
            'iSCSI'
            ```
        """
        if not self.scsi_id:
            return None

        try:
            result = run(f'lsscsi {self.scsi_id} --list -t | grep transport')
            if result.succeeded:
                for line in result.stdout.splitlines():
                    if 'transport' in line:
                        return line.split('=')[1].strip()
                    return None
        except (OSError, IndexError):
            return None

    @property
    def driver(self) -> str | None:
        """Get device driver.

        Returns:
            Device driver or None if not available

        Example:
            ```Python
            device.driver
            'qla2xxx'
            ```
        """
        if not self.host_id:
            return None

        try:
            result = run(f'lsscsi -H {self.host_id}')
            if result.succeeded and len(result.stdout.split()) > 1:
                return result.stdout.split()[1]
        except (OSError, IndexError):
            logging.warning(f'Failed to get the driver for host {self.host_id}.')
            return None
        else:
            return None

    @property
    def state(self) -> str | None:
        """Get device state.

        Returns:
            The state of the device or None if not available

        """
        state_path = Path(f'{self.BLOCK_PATH}/{self.name}/device/state')
        try:
            return state_path.read_text().strip()
        except OSError:
            logging.warning(f'Failed to read {state_path}')
            return None

    @property
    def pci_id(self) -> str | None:
        """Get the PCI ID associated with the SCSI host.

        Returns:
            PCI ID or None if not available

        Example:
            ```Python
            device.pci_id
            '0000:08:00.0'
            ```
        """
        if not self.host_id:
            return None

        scsi_host_path = Path(f'{self.SCSI_HOST_PATH}/host{self.host_id}')
        try:
            link = scsi_host_path.resolve().as_posix()
        except OSError as e:
            logging.warning(f'Error resolving path for host{self.host_id}: {e}')
            return None
        else:
            regex_pci_id = r'([0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f])'
            pci_match = re.search(f'{regex_pci_id}/host{self.host_id}/scsi_host', link)
            return pci_match.group(1) if pci_match else None

    def rescan_host(self) -> bool:
        """Initiates a rescan operation for the specified host ID, to detect new devices.

        The scan file is part of the sysfs interface in Linux, which exposes kernel data structures to user space.
        Writing - - - to this file instructs the kernel to scan all channels, all targets, and all LUNs
        for the specified host adapter.

        Returns:
            True if the rescan operation is successful, False otherwise.
        """
        if not self.host_id:
            return False

        rescan_path = Path(f'{self.SCSI_HOST_PATH}/host{self.host_id}/scan')
        try:
            rescan_path.write_text('- - -')
        except OSError:
            logging.warning(f'Failed to write to {rescan_path}.')
            return False
        else:
            return True

    def rescan_disk(self) -> bool:
        """Rescan the disk.

        Returns:
            True if the rescan operation is successful, otherwise False.

        """
        rescan_path = Path(f'{self.BLOCK_PATH}/{self.name}/device/rescan')
        try:
            rescan_path.write_text('1')
        except OSError:
            logging.warning(f'Failed to write to {rescan_path}.')
            return False
        else:
            return True

    def delete_disk(self) -> bool:
        """Deletes the disk.

        Returns:
            True if the disk device is successfully deleted, otherwise False.

        """
        del_path = Path(f'{self.BLOCK_PATH}/{self.name}/device/delete')
        try:
            del_path.write_text('1')
        except OSError:
            logging.warning(f'Failed to write to {del_path}.')
            return False
        else:
            return True

    def up_or_down_disk(self, action: str) -> bool:
        """Change the state of the disk.

        Args:
            action: offline or running.

        Returns:
            True if the operation is successful, otherwise returns False.

        """
        state_path = Path(f'{self.BLOCK_PATH}/{self.name}/device/state')
        try:
            # Need a newline character at the end of the action, or else it cannot be written into
            action = f'{action}\n'
            state_path.write_text(action)
        except OSError:
            logging.warning(f'Failed to write to {state_path}')
            return False
        else:
            return True

    @classmethod
    def get_all_scsi_device_ids(cls) -> list[str]:
        """Get the list of all SCSI device IDs.

        Returns:
            List of SCSI device IDs

        Example:
            '''Python
            ScsiDevice.get_all_scsi_device_ids()
            ['7:0:0:0', '8:0:0:0', '7:0:0:1',...]
            '''

        """
        try:
            path = cls.SCSI_PATH
            if path.exists():
                return [d.name for d in path.iterdir()]
        except OSError:
            logging.warning(f'Failed to list SCSI devices from {cls.SCSI_PATH}')
            return []
        else:
            return []

    @classmethod
    def get_all_scsi_devices(cls: type[T]) -> list[T]:
        """Retrieve all SCSI devices.

        Returns:
            A list of ScsiDevice objects, each representing a SCSI device.

        Example:
            ```Python
            ScsiDevice.get_all_scsi_devices()
            [ScsiDevice(path='/dev/sda', name='sda', ...), ScsiDevice(path='/dev/sdb', name='sdb',...),...]
            ```

        """
        scsi_ids = ScsiDevice.get_all_scsi_device_ids()
        devices: list[T] = [cls(scsi_id=scsi_id) for scsi_id in scsi_ids]
        return devices

    @classmethod
    def get_by_vendor(cls: type[T], vendor: str) -> list[T]:
        """Retrieve a list of ScsiDevice objects that match the specified vendor.

        Args:
            vendor (str): used to filter the SCSI devices.

        Returns:
            A list of ScsiDevice objects.

        Example:
            ```Python
            ScsiDevice.get_by_vendor('NETAPP')
            [ScsiDevice(path='/dev/sdb', name='sdb', ...), ScsiDevice(path='/dev/sdc', ...), ...]
            ```

        """
        all_devices = cls.get_all_scsi_devices()
        return [device for device in all_devices if device.vendor == vendor]

    @classmethod
    def get_by_attribute(cls: type[T], attribute: str, value: str) -> list[T]:
        """Retrieve a list of ScsiDevice objects that match the specified attribute and value.

        Args:
            attribute (str): The attribute used to filter the SCSI devices (e.g., 'transport', 'vendor').
            value (str): The value of the attribute used to filter the SCSI devices.

        Returns:
            A list of ScsiDevice objects.

        Example:
            ```Python
            ScsiDevice.get_by_attribute('transport', 'fc:')
            [ScsiDevice(path='/dev/sdb', name='sdb', ...), ScsiDevice(path='/dev/sdc', ...), ...]

            ScsiDevice.get_by_attribute('vendor', 'NETAPP')
            [ScsiDevice(path='/dev/sdb', name='sdb', ...), ScsiDevice(path='/dev/sdc', ...), ...]
        """
        all_devices = cls.get_all_scsi_devices()
        return [device for device in all_devices if getattr(device, attribute, None) == value]
