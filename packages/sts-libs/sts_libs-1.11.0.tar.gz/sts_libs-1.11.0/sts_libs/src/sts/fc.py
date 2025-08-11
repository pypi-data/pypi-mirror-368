# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fibre Channel device management.

This module provides functionality for managing FC devices:
- Host management
- Remote port management
- WWN handling
- Device discovery
- Transport type detection

Fibre Channel (FC) is a high-speed network technology used for:
- Storage Area Networks (SAN)
- Block-level data transfer
- Enterprise storage connectivity

Key concepts:
- WWN (World Wide Name): Unique device identifier
- Host Bus Adapter (HBA): FC network interface
- Ports: Physical or virtual FC connections
- Zoning: Access control between devices
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Literal

from sts.scsi import ScsiDevice
from sts.utils.cmdline import run
from sts.utils.errors import DeviceError

# WWN format: 8 pairs of hex digits separated by colons
WWN_PATTERN = re.compile(r'(?:[0-9a-f]{2}:){7}[0-9a-f]{2}')

# FC transport types:
# - FC: Traditional Fibre Channel
# - FCoE: Fibre Channel over Ethernet
TransportType = Literal['FC', 'FCoE']


@dataclass
class FcDevice(ScsiDevice):
    """Fibre Channel device representation.

    A Fibre Channel device is identified by:
    - WWN (World Wide Name): Unique identifier
    - Host ID: Local HBA identifier
    - Remote ports: Connected target ports
    - Transport type: FC or FCoE

    Device discovery uses:
    - sysfs entries (/sys/class/fc_*)
    - HBA driver information
    - SCSI subsystem links

    Args:
        name: Device name (optional, e.g. 'sda')
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        wwn: World Wide Name (optional, discovered from device)
        host_id: FC host ID (optional, discovered from device)
        transport_type: Transport type (optional, discovered from device)

    Example:
        ```python
        device = FcDevice(name='sda')  # Discovers other values
        device = FcDevice(wwn='10:00:5c:b9:01:c1:ec:71')  # Discovers device from WWN
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None
    scsi_id: str | None = None  # SCSI address (H:C:T:L)
    host_id: str | None = None  # Local HBA ID

    # Optional parameters for this class
    wwn: str | None = None  # World Wide Name
    transport_type: TransportType | None = None  # FC or FCoE

    # Internal fields
    _remote_ports: list[str] = field(init=False, default_factory=list)

    # Sysfs paths for FC information
    HOST_PATH: ClassVar[Path] = Path('/sys/class/fc_host')
    REMOTE_PORT_PATH: ClassVar[Path] = Path('/sys/class/fc_remote_ports')

    def __post_init__(self) -> None:
        """Initialize FC device.

        Discovery process:
        1. Set device path if needed
        2. Find host ID from SCSI device link
        3. Get WWN from host information
        4. Determine transport type
        5. Validate WWN format

        Raises:
            DeviceError: If device cannot be initialized
        """
        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = Path(f'/dev/{self.name}')

        # Initialize parent class
        super().__post_init__()

        # Discover host_id from SCSI device link
        if not self.host_id and self.name:
            sys_block_dev_path = Path(f'{self.BLOCK_PATH}/{self.name}/device')
            if sys_block_dev_path.exists():
                # Extract host ID from symlink like:
                # /sys/devices/pci0000:00/0000:00:03.0/0000:08:00.0/host7/rport-7:0-0/target7:0:0/7:0:0:1
                match = re.search(r'host(\d+)', str(sys_block_dev_path.resolve()))
                if match:
                    self.host_id = match.group(1).strip()

        # Discover WWN from host information
        if not self.wwn and self.host_id:
            self.wwn = self.get_host_wwn(self.host_id)

        # Discover transport type from host
        if not self.transport_type and self.host_id:
            self.transport_type = self.get_host_transport_type(self.host_id)

        # Validate WWN format if provided
        if self.wwn and not self.is_valid_wwn(self.wwn):
            raise DeviceError(f'Invalid WWN format: {self.wwn}')

    @staticmethod
    def is_valid_wwn(wwn: str) -> bool:
        """Check if WWN is valid.

        WWN format: 8 pairs of hex digits separated by colons
        Example:
            ```python
            10:00:5c:b9:01:c1:ec:71

        Args:
                wwn: World Wide Name to check

        Returns:
                True if valid, False otherwise

        Example:
                FcDevice.is_valid_wwn('10:00:5c:b9:01:c1:ec:71')
                True
            ```
        """
        return bool(WWN_PATTERN.match(wwn.lower()))

    @staticmethod
    def standardize_wwn(wwn: str) -> str | None:
        """Standardize WWN format.

        Converts various WWN formats to standard format:
        - Removes '0x' prefix
        - Converts to lowercase
        - Adds colons between pairs
        - Validates final format

        Args:
            wwn: World Wide Name to standardize

        Returns:
            Standardized WWN or None if invalid

        Example:
            ```python
            FcDevice.standardize_wwn('500A0981894B8DC5')
            '50:0a:09:81:89:4b:8d:c5'
            ```
        """
        if not wwn:
            return None

        # Remove 0x and : characters
        wwn = re.sub('0x', '', wwn.lower()).replace(':', '')

        # Add : every 2 characters
        wwn = ':'.join(wwn[i : i + 2] for i in range(0, len(wwn), 2))

        return wwn if FcDevice.is_valid_wwn(wwn) else None

    @property
    def remote_ports(self) -> list[str]:
        """Get remote ports.

        Lists FC ports connected to this host:
        - Format: rport-H:B-R
          - H: Host number
          - B: Bus number
          - R: Remote port number

        Returns:
            List of remote port IDs

        Example:
            ```python
            device.remote_ports
            ['rport-0:0-1', 'rport-0:0-2']
            ```
        """
        if not self._remote_ports and self.host_id:
            result = run(f'ls {self.REMOTE_PORT_PATH} | grep rport-{self.host_id}')
            if result.succeeded:
                self._remote_ports = result.stdout.splitlines()
        return self._remote_ports

    def get_remote_port_wwn(self, port: str) -> str | None:
        """Get WWN of remote port.

        Reads port_name from sysfs:
        - Standardizes WWN format
        - Validates WWN format
        - Returns None if invalid

        Args:
            port: Remote port ID (e.g. 'rport-0:0-1')

        Returns:
            WWN of remote port or None if not found

        Example:
            ```python
            device.get_remote_port_wwn('rport-0:0-1')
            '20:00:5c:b9:01:c1:ec:71'
            ```
        """
        result = run(f'cat {self.REMOTE_PORT_PATH}/{port}/port_name')
        if result.failed:
            return None
        return self.standardize_wwn(result.stdout.strip())

    def get_remote_port_param(self, port: str, param: str) -> str | None:
        """Get remote port parameter.

        Common parameters:
        - dev_loss_tmo: Device loss timeout
        - fast_io_fail_tmo: Fast I/O failure timeout
        - node_name: FC node name
        - port_state: Port state (Online/Offline)

        Args:
            port: Remote port ID (e.g. 'rport-0:0-1')
            param: Parameter name

        Returns:
            Parameter value or None if not found

        Example:
            ```python
            device.get_remote_port_param('rport-0:0-1', 'dev_loss_tmo')
            '60'
            ```
        """
        result = run(f'cat {self.REMOTE_PORT_PATH}/{port}/{param}')
        if result.failed:
            return None
        return result.stdout.strip()

    def set_remote_port_param(self, port: str, param: str, value: str) -> bool:
        """Set remote port parameter.

        Configures port behavior:
        - Timeout values
        - Port states
        - Operating parameters

        Args:
            port: Remote port ID (e.g. 'rport-0:0-1')
            param: Parameter name
            value: Parameter value

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.set_remote_port_param('rport-0:0-1', 'dev_loss_tmo', '60')
            True
            ```
        """
        result = run(f'echo {value} > {self.REMOTE_PORT_PATH}/{port}/{param}')
        return result.succeeded

    @classmethod
    def get_hosts(cls) -> list[str]:
        """Get list of FC hosts.

        Lists all FC HBAs in the system:
        - Traditional FC HBAs
        - FCoE CNAs
        - Virtual HBAs

        Returns:
            List of host IDs

        Example:
            ```python
            FcDevice.get_hosts()
            ['0', '1']
            ```
        """
        result = run(f'ls {cls.HOST_PATH}')
        if result.failed:
            return []
        return [h.removeprefix('host') for h in result.stdout.splitlines()]

    @classmethod
    def get_host_wwn(cls, host_id: str) -> str | None:
        """Get WWN of FC host.

        Reads port_name from sysfs:
        - Standardizes WWN format
        - Validates WWN format
        - Returns None if invalid

        Args:
            host_id: Host ID

        Returns:
            WWN of host or None if not found

        Example:
            ```python
            FcDevice.get_host_wwn('0')
            '10:00:5c:b9:01:c1:ec:71'
            ```
        """
        result = run(f'cat {cls.HOST_PATH}/host{host_id}/port_name')
        if result.failed:
            return None
        return cls.standardize_wwn(result.stdout.strip())

    @classmethod
    def get_host_transport_type(cls, host_id: str) -> TransportType | None:
        """Get transport type of FC host.

        Determines type through multiple methods:
        1. Model name matching
        2. Symbolic name inspection
        3. Driver name checking

        Args:
            host_id: Host ID

        Returns:
            Transport type or None if not found

        Example:
            ```python
            FcDevice.get_host_transport_type('0')
            'FC'
            ```
        """
        # Common model to transport type mapping
        model_map: dict[str, TransportType] = {
            'QLE2462': 'FC',  # QLogic 4Gb FC
            'QLE2772': 'FC',  # QLogic 32Gb FC
            'QLE8262': 'FCoE',  # QLogic 10Gb FCoE
            'QLE8362': 'FCoE',  # QLogic 10Gb FCoE
            'CN1000Q': 'FCoE',  # Cavium/QLogic FCoE
            'QLogic-1020': 'FCoE',  # QLogic FCoE
            '554FLR-SFP+': 'FCoE',  # HP FCoE
            'Intel 82599': 'FCoE',  # Intel FCoE
        }

        # Try to get model from sysfs
        result = run(f'cat {cls.HOST_PATH}/host{host_id}/model_name')
        if result.succeeded:
            model = result.stdout.strip()
            if model in model_map:
                return model_map[model]

        # Try to get from symbolic name
        result = run(f'cat {cls.HOST_PATH}/host{host_id}/symbolic_name')
        if result.succeeded:
            name = result.stdout.lower()
            if 'fibre channel' in name:
                return 'FC'
            if 'fcoe' in name:
                return 'FCoE'

        # Try to get from driver
        result = run(f'cat {cls.HOST_PATH}/host{host_id}/driver_name')
        if result.succeeded:
            driver = result.stdout.strip()
            if driver in {'bnx2fc', 'qedf'}:  # FCoE drivers
                return 'FCoE'

        return None

    @classmethod
    def get_all(cls) -> list[FcDevice]:
        """Get list of all FC devices.

        Discovery process:
        1. Find all FC hosts
        2. Get targets for each host
        3. Extract device names
        4. Create device objects

        Returns:
            List of FcDevice instances

        Example:
            ```python
            FcDevice.get_all()
            [FcDevice(name='sda', ...), FcDevice(name='sdb', ...)]
            ```
        """
        # Get all FC hosts
        hosts = cls.get_hosts()

        # Get all targets for each host
        all_targets: list[tuple[str, str]] = []
        for host_id in hosts:
            result = run(f'ls -1 /sys/class/fc_host/host{host_id}/device/target*')
            if result.succeeded:
                all_targets.extend((target, host_id) for target in result.stdout.splitlines())

        # Extract device names from target paths
        device_info: list[tuple[str, str]] = []
        for target, host_id in all_targets:
            name = Path(target).name
            if name:
                device_info.append((name, host_id))
            else:
                logging.warning(f'Invalid target path: {target}')

        # Create device objects with host information
        return [cls(name=name, host_id=host_id) for name, host_id in device_info]
