# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Network interface management.

This module provides functionality for managing network interfaces:
- Interface discovery
- MAC address handling
- IP address management
- Interface operations
"""

from __future__ import annotations

import ipaddress
import logging
import re
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal

from sts.network.errors import NetworkError
from sts.utils.cmdline import run

# Constants
MAC_ADDRESS_LENGTH = 12  # Length of MAC address without colons

# MAC address regex pattern (e.g. F0:DE:F1:0D:D3:C9)
MAC_PATTERN = re.compile(r'^(?:[0-9A-F]{2}:){5}[0-9A-F]{2}$', re.IGNORECASE)


@dataclass
class NetworkInterface:
    """Network interface representation.

    This class provides functionality for managing network interfaces:
    - Interface discovery
    - MAC address handling
    - IP address management
    - Interface operations

    Args:
        name: Interface name (optional, discovered from MAC)
        mac: MAC address (optional, discovered from name)
        driver: Driver name (optional, discovered from interface)
        pci_id: PCI ID (optional, discovered from interface)

    Example:
        ```python
        iface = NetworkInterface()  # Discovers first available interface
        iface = NetworkInterface(name='eth0')  # Discovers other values
        iface = NetworkInterface(mac='F0:DE:F1:0D:D3:C9')  # Discovers other values
        ```
    """

    # Optional parameters
    name: str | None = None
    mac: str | None = None
    driver: str | None = None
    pci_id: str | None = None

    # Class-level paths
    SYSFS_PATH: ClassVar[Path] = Path('/sys/class/net')

    def __post_init__(self) -> None:
        """Initialize network interface.

        Discovers name, MAC, driver, and PCI ID if not provided.
        """
        # Discover first available interface if no parameters provided
        if not any([self.name, self.mac]):
            result = run('ls /sys/class/net')
            if result.succeeded:
                for name in result.stdout.splitlines():
                    # Skip special interfaces
                    if any(re.match(pattern, name) for pattern in self._get_skip_patterns()):
                        continue
                    self.name = name
                    break

        # Discover interface info if needed
        if self.name:
            # Get MAC address if not provided
            if not self.mac:
                mac_result = run(f'ip -o link show {self.name}')
                if mac_result.succeeded:
                    with suppress(IndexError):
                        mac = mac_result.stdout.split()[15]
                        if self.is_valid_mac(mac):
                            self.mac = mac

            # Get driver if not provided
            if not self.driver:
                driver_path = self.SYSFS_PATH / self.name / 'device/driver'
                if driver_path.exists():
                    self.driver = driver_path.resolve().name

            # Get PCI ID if not provided
            if not self.pci_id:
                device_path = self.SYSFS_PATH / self.name
                if device_path.exists():
                    link = device_path.resolve().as_posix()
                    pci_match = re.search(r'([0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f])/net', link)
                    if pci_match:
                        self.pci_id = pci_match.group(1)

        # Discover interface by MAC if provided
        elif self.mac:
            if not self.is_valid_mac(self.mac):
                raise NetworkError(f'Invalid MAC format: {self.mac}')
            for interface in self.get_all():
                if interface.mac and self.mac and interface.mac.upper() == self.mac.upper():
                    self.name = interface.name
                    self.driver = interface.driver
                    self.pci_id = interface.pci_id
                    break

        # Validate MAC if provided
        elif self.mac and not self.is_valid_mac(self.mac):
            raise NetworkError(f'Invalid MAC format: {self.mac}')

    @staticmethod
    def _get_skip_patterns() -> list[str]:
        """Get patterns for interfaces to skip.

        Returns:
            List of regex patterns
        """
        return [
            r'^lo$',  # Loopback
            r'^tun[0-9]+$',  # TUN/TAP
            r'^vboxnet[0-9]+$',  # VirtualBox
            r'\.',  # Sub-interfaces
        ]

    @staticmethod
    def is_valid_mac(mac: str) -> bool:
        """Check if MAC address is valid.

        Args:
            mac: MAC address to check

        Returns:
            True if valid, False otherwise

        Example:
            ```python
            NetworkInterface.is_valid_mac('F0:DE:F1:0D:D3:C9')
            True
            ```
        """
        return bool(MAC_PATTERN.match(mac))

    @staticmethod
    def standardize_mac(mac: str) -> str | None:
        """Standardize MAC address format.

        Args:
            mac: MAC address to standardize

        Returns:
            Standardized MAC or None if invalid

        Example:
            ```python
            NetworkInterface.standardize_mac('F0-DE-F1-0D-D3-C9')
            'F0:DE:F1:0D:D3:C9'
            ```
        """
        if not mac:
            return None

        # Remove 0x and non-hex characters
        mac = re.sub('^0x', '', mac.upper())
        mac = re.sub('[^0-9A-F]', '', mac)

        # Add : every 2 characters
        if len(mac) == MAC_ADDRESS_LENGTH:
            mac = ':'.join(mac[i : i + 2] for i in range(0, MAC_ADDRESS_LENGTH, 2))

        return mac if NetworkInterface.is_valid_mac(mac) else None

    @property
    def ip_addresses(self) -> list[str]:
        """Get IP addresses.

        Returns:
            List of IP addresses

        Example:
            ```python
            iface.ip_addresses
            ['192.168.1.100', 'fe80::1234:5678:9abc:def0']
            ```
        """
        if not self.name:
            return []

        result = run(f'ip addr show {self.name}')
        if result.failed:
            return []

        addresses = []
        for line in result.stdout.splitlines():
            if 'inet' in line:
                # Parse line like: inet 192.168.1.100/24
                try:
                    addr = line.split()[1].split('/')[0]
                    addresses.append(addr)
                except (IndexError, ValueError):
                    continue

        return addresses

    def get_ip_version(self, addr: str) -> Literal[4, 6] | None:
        """Get IP version.

        Args:
            addr: IP address

        Returns:
            4 for IPv4, 6 for IPv6, None if invalid

        Example:
            ```python
            iface.get_ip_version('192.168.1.100')
            4
            ```
        """
        try:
            return ipaddress.ip_address(addr).version
        except ValueError:
            return None

    def up(self) -> bool:
        """Bring interface up.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            iface.up()
            True
            ```
        """
        if not self.name:
            logging.error('Interface name required')
            return False

        result = run(f'ip link set {self.name} up')
        return result.succeeded

    def down(self) -> bool:
        """Bring interface down.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            iface.down()
            True
            ```
        """
        if not self.name:
            logging.error('Interface name required')
            return False

        result = run(f'ip link set {self.name} down')
        return result.succeeded

    @classmethod
    def get_all(cls) -> list[NetworkInterface]:
        """Get list of all network interfaces.

        Returns:
            List of NetworkInterface instances

        Example:
            ```python
            NetworkInterface.get_all()
            [NetworkInterface(name='eth0', ...), NetworkInterface(name='eth1', ...)]
            ```
        """
        interfaces: list[NetworkInterface] = []

        # Get all interfaces
        result = run('ls /sys/class/net')
        if result.failed:
            return interfaces

        for name in result.stdout.splitlines():
            # Skip special interfaces
            if any(re.match(pattern, name) for pattern in cls._get_skip_patterns()):
                continue

            # Create interface
            try:
                interface = cls(name=name)
                if interface.mac:  # Only add if MAC was discovered
                    interfaces.append(interface)
            except (OSError, ValueError, NetworkError) as e:
                logging.warning(f'Failed to create interface: {e}')

        return interfaces

    @classmethod
    def get_by_mac(cls, mac: str) -> NetworkInterface | None:
        """Get interface by MAC address.

        Args:
            mac: MAC address

        Returns:
            NetworkInterface instance or None if not found

        Example:
            ```python
            NetworkInterface.get_by_mac('F0:DE:F1:0D:D3:C9')
            NetworkInterface(name='eth0', ...)
            ```
        """
        std_mac = cls.standardize_mac(mac)
        if not std_mac:
            return None

        try:
            return cls(mac=std_mac)
        except NetworkError:
            return None

    @classmethod
    def get_by_ip(cls, ip: str) -> NetworkInterface | None:
        """Get interface by IP address.

        Args:
            ip: IP address

        Returns:
            NetworkInterface instance or None if not found

        Example:
            ```python
            NetworkInterface.get_by_ip('192.168.1.100')
            NetworkInterface(name='eth0', ...)
            ```
        """
        for interface in cls.get_all():
            if ip in interface.ip_addresses:
                return interface

        return None
