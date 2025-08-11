# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""RDMA device management.

This module provides functionality for managing RDMA devices:
- Device discovery and configuration
- Port management and link status
- SR-IOV (Single Root I/O Virtualization)
- Power management

RDMA (Remote Direct Memory Access) enables:
- Zero-copy data transfer
- Kernel bypass for low latency
- CPU offload for better performance
- Hardware-based reliability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

# Base path for RDMA devices in sysfs
RDMA_SYSFS_BASE = '/sys/class/infiniband/'


def exists_rdma() -> bool:
    """Check whether system has RDMA devices.

    RDMA devices appear under /sys/class/infiniband/ when:
    - Hardware supports RDMA (InfiniBand, RoCE, iWARP)
    - Required drivers are loaded
    - Device is properly configured

    Returns:
        True if RDMA devices exist, False otherwise
    """
    return Path(RDMA_SYSFS_BASE).is_dir()


def exists_device(ibdev: str) -> bool:
    """Check whether specific RDMA device exists.

    Args:
        ibdev: RDMA device ID (e.g., 'mlx5_0')

    Returns:
        True if device exists, False otherwise
    """
    return Path(f'{RDMA_SYSFS_BASE}{ibdev}').is_dir()


@dataclass
class Port:
    """RDMA port representation.

    A port represents a physical network connection that:
    - Has specific link rate (speed)
    - Can be in different states
    - Supports various link widths
    - Reports physical status

    Link rates:
    - SDR (Single Data Rate): 2.5 Gb/s per lane
    - DDR (Double Data Rate): 5 Gb/s per lane
    - QDR (Quad Data Rate): 10 Gb/s per lane
    - FDR (Fourteen Data Rate): 14 Gb/s per lane
    - EDR (Enhanced Data Rate): 25 Gb/s per lane
    - HDR (High Data Rate): 50 Gb/s per lane

    Args:
        path: Port sysfs path
    """

    path: Path
    name: str = field(init=False)
    rate: str | None = field(init=False, default=None)  # Link rate (e.g., '100 Gb/sec (4X EDR)')
    state: str | None = field(init=False, default=None)  # Port state (e.g., '4: ACTIVE')
    phys_state: str | None = field(init=False, default=None)  # Physical state (e.g., '5: LinkUp')
    rate_speed: str | None = field(init=False, default=None)  # Numeric rate (e.g., '100')
    rate_unit: str | None = field(init=False, default=None)  # Rate unit (e.g., 'Gb/sec')
    rate_info: str | None = field(init=False, default=None)  # Link info (e.g., '4X EDR')
    state_num: str | None = field(init=False, default=None)  # State number (e.g., '4')
    state_str: str | None = field(init=False, default=None)  # State string (e.g., 'ACTIVE')
    phys_state_num: str | None = field(init=False, default=None)  # Physical state number (e.g., '5')
    phys_state_str: str | None = field(init=False, default=None)  # Physical state string (e.g., 'LinkUp')

    def __post_init__(self) -> None:
        """Initialize port attributes from sysfs.

        Reads and parses:
        - Port name
        - Link rate and width
        - Port state
        - Physical state
        """
        self.name = self.path.name

        # Read all sysfs attributes
        for param in self.path.iterdir():
            if param.is_file():
                try:
                    setattr(self, param.stem, param.read_text().strip())
                except OSError:
                    continue

        # Parse rate into components
        if self.rate:
            # Example: '100 Gb/sec (4X EDR)'
            rate_split = self.rate.split()
            self.rate_speed = rate_split[0]  # Numeric rate
            self.rate_unit = rate_split[1]  # Rate unit
            # Keep original format for link width and type
            self.rate_info = f'{rate_split[2].strip("(")} {rate_split[3].strip(")")}'

        # Parse port state
        if self.state:
            self.state_num = self.state.split(':')[0]
            self.state_str = self.state.split(': ')[1]

        # Parse physical state
        if self.phys_state:
            self.phys_state_num = self.phys_state.split(':')[0]
            self.phys_state_str = self.phys_state.split(': ')[1]


@dataclass
class Power:
    """RDMA power management.

    Controls device power states:
    - Runtime power management
    - System suspend/resume
    - Power saving features

    Power states:
    - D0: Fully powered and operational
    - D1/D2: Intermediate power states
    - D3hot: Low power, context preserved
    - D3cold: Powered off

    Args:
        path: Device sysfs path
    """

    path: Path

    def __post_init__(self) -> None:
        """Initialize power attributes from sysfs.

        Reads power management settings:
        - Current power state
        - Available power states
        - Control settings
        """
        power_path = self.path / 'power'
        if power_path.is_dir():
            for param in power_path.iterdir():
                if param.is_file():
                    try:
                        value = param.read_text()
                    except OSError:
                        continue
                    setattr(self, param.stem, value.strip())


@dataclass
class NetDev:
    """RDMA network device.

    Represents the network interface associated with:
    - RDMA device
    - Specific port
    - Network configuration

    Args:
        path: Device sysfs path
    """

    path: Path
    dev_port: str | None = field(init=False, default=None)  # Associated port number

    def __post_init__(self) -> None:
        """Initialize network device attributes from sysfs.

        Reads network interface settings:
        - Port association
        - Device parameters
        """
        for param in self.path.iterdir():
            if param.is_file():
                try:
                    value = param.read_text()
                except OSError:
                    continue
                setattr(self, param.stem, value.strip())


@dataclass
class Sriov:
    """SR-IOV configuration.

    SR-IOV (Single Root I/O Virtualization):
    - Allows one physical device to appear as multiple virtual devices
    - Physical Function (PF) is the main device
    - Virtual Functions (VFs) are lightweight instances
    - Each VF appears as a separate PCI device
    - VFs can be assigned to VMs or containers

    Benefits:
    - Hardware-based virtualization
    - Near-native performance
    - Reduced CPU overhead
    - Better isolation

    Args:
        path: Device sysfs path
    """

    path: Path
    sriov_numvfs: str | None = field(init=False, default=None)  # Current number of VFs
    sriov_totalvfs: str | None = field(init=False, default=None)  # Maximum VFs supported
    sriov_numvfs_path: Path = field(init=False)  # Path to numvfs control

    def __post_init__(self) -> None:
        """Initialize SR-IOV attributes from sysfs.

        Reads SR-IOV configuration:
        - Current VF count
        - Maximum VFs supported
        - Control file location
        """
        self.sriov_numvfs_path = self.path / 'sriov_numvfs'

        if self.path.is_dir():
            for param in self.path.iterdir():
                if param.is_file():
                    try:
                        value = param.read_text()
                    except (OSError, UnicodeDecodeError):
                        continue
                    setattr(self, param.stem, value.strip())

    def set_numvfs(self, num: str = '1') -> None:
        """Set number of Virtual Functions.

        VF allocation process:
        1. Reset current VFs (write 0)
        2. Allocate new VFs (write desired number)
        3. Update internal state

        Args:
            num: Number of VFs to allocate (default: '1')

        Example:
            ```python
            sriov.set_numvfs('4')  # Create 4 VFs
            ```
        """
        if self.sriov_numvfs and num != self.sriov_numvfs:
            self.sriov_numvfs_path.write_text('0')  # Reset VFs
            self.sriov_numvfs_path.write_text(num)  # Allocate new VFs
            self.sriov_numvfs = self.read_numvfs()  # Update state

    def read_numvfs(self) -> str | None:
        """Read current number of Virtual Functions.

        Returns:
            Number of VFs or None if not available

        Example:
            ```python
            sriov.read_numvfs()
            '4'  # 4 VFs currently allocated
            ```
        """
        return self.sriov_numvfs_path.read_text().strip() if self.sriov_numvfs_path.is_file() else None


@dataclass
class RdmaDevice:
    """RDMA device representation.

    Manages RDMA device features:
    - Port configuration and status
    - Network interface association
    - SR-IOV capability and control
    - Power management

    Device types:
    - InfiniBand (Native RDMA)
    - RoCE (RDMA over Converged Ethernet)
    - iWARP (Internet Wide Area RDMA Protocol)

    Args:
        ibdev: Device ID (e.g., 'mlx5_0') or full path

    Example:
        ```python
        device = RdmaDevice('mlx5_0')  # Mellanox ConnectX-5
        device.exists
        True
        ```
    """

    # Class-level paths
    RDMA_PATH: ClassVar[Path] = Path(RDMA_SYSFS_BASE)

    # Instance variables
    ibdev: str  # Device identifier
    _path: Path = field(init=False)  # Base sysfs path
    ports_path: Path = field(init=False)  # Path to ports directory
    device_path: Path = field(init=False)  # Path to PCI device
    net_path: Path = field(init=False)  # Path to network interfaces
    ports: list[Path] = field(init=False, default_factory=list)  # Available ports
    port_numbers: list[str] = field(init=False, default_factory=list)  # Port numbers
    is_sriov_capable: bool = field(init=False, default=False)  # SR-IOV support

    def __post_init__(self) -> None:
        """Initialize device attributes from sysfs.

        Discovers:
        - Device paths and attributes
        - Available ports
        - SR-IOV capability
        """
        # Set up base path
        self._path = Path(f'{RDMA_SYSFS_BASE}{self.ibdev}')

        # Read device attributes
        for param in self._path.iterdir():
            if param.is_file():
                try:
                    setattr(self, param.stem, param.read_text().strip())
                except OSError:
                    continue

        # Initialize component paths
        self.ports_path = self._path / 'ports'
        self.device_path = (self._path / 'device').resolve()
        self.net_path = self.device_path / 'net'

        # Discover ports
        self.ports = [port for port in self.ports_path.iterdir() if port.is_dir()]
        self.port_numbers = [port.name for port in self.ports]

        # Check SR-IOV support
        self.is_sriov_capable = (self.device_path / 'sriov_numvfs').is_file()

    def get_netdevs(self) -> list[NetDev]:
        """Get network devices.

        Returns:
            List of associated network interfaces

        Example:
            ```python
            device.get_netdevs()
            [NetDev(path=/sys/class/net/eth0), ...]  # Network interfaces
            ```
        """
        return [NetDev(eth) for eth in self.net_path.iterdir() if eth.is_dir()]

    def get_netdev(self, port_id: str) -> NetDev | None:
        """Get network device by port ID.

        Args:
            port_id: Port ID (1-based)

        Returns:
            Network device or None if not found

        Example:
            ```python
            device.get_netdev('1')  # Get interface for port 1
            NetDev(path=/sys/class/net/eth0)
            ```
        """
        for dev in self.get_netdevs():
            if dev.dev_port == str(int(port_id) - 1):  # Convert to 0-based index
                return dev
        return None

    def get_ports(self) -> list[Port] | None:
        """Get all ports.

        Returns:
            List of ports or None if no ports

        Example:
            ```python
            device.get_ports()
            [Port(path=/sys/.../ports/1), ...]  # All available ports
            ```
        """
        return [Port(port) for port in self.ports] if self.ports else None

    def get_port(self, port: str) -> Port | None:
        """Get port by number.

        Args:
            port: Port number

        Returns:
            Port or None if not found

        Example:
            ```python
            device.get_port('1')  # Get port 1
            Port(path=/sys/.../ports/1)
            ```
        """
        path = self.ports_path / port
        return Port(path) if path.is_dir() else None

    def get_power(self) -> Power:
        """Get power management interface.

        Returns:
            Power management interface

        Example:
            ```python
            device.get_power()  # Get power management
            Power(path=/sys/class/infiniband/mlx5_0)
            ```
        """
        return Power(self._path)

    def get_sriov(self) -> Sriov | None:
        """Get SR-IOV configuration interface.

        Returns:
            SR-IOV interface or None if not supported

        Example:
            ```python
            device.get_sriov()  # Get SR-IOV if supported
            Sriov(path=/sys/.../device)
            ```
        """
        return Sriov(self.device_path) if self.is_sriov_capable else None
