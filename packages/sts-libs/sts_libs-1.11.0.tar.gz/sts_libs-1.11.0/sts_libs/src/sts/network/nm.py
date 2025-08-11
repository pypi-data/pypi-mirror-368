# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""NetworkManager operations.

This module provides functionality for managing NetworkManager:
- Connection management
- Interface configuration
- Network settings
"""

from __future__ import annotations

import ipaddress
import logging
from contextlib import suppress
from dataclasses import dataclass
from typing import Literal, TypedDict

from sts.network.interface import NetworkInterface
from sts.utils.cmdline import run

# Constants
IPV4_VERSION = 4

# Connection types
ConnectionType = Literal['ethernet', 'wifi', 'bond', 'bridge', 'team', 'vlan']


class ConnectionSettings(TypedDict, total=False):
    """NetworkManager connection settings.

    Common settings include:
    - ipv4.method: Connection method (e.g. 'auto', 'manual')
    - ipv4.addresses: IP addresses
    - ipv4.gateway: Gateway address
    - ipv4.dns: DNS servers
    """

    # IPv4 settings
    ipv4_method: str  # ipv4.method
    ipv4_addresses: str  # ipv4.addresses
    ipv4_gateway: str  # ipv4.gateway
    ipv4_dns: str  # ipv4.dns

    # IPv6 settings
    ipv6_method: str  # ipv6.method
    ipv6_addresses: str  # ipv6.addresses
    ipv6_gateway: str  # ipv6.gateway
    ipv6_dns: str  # ipv6.dns

    # Connection settings
    autoconnect: str  # connection.autoconnect
    interface_name: str  # connection.interface-name


def _convert_setting_name(key: str) -> str:
    """Convert Python setting name to nmcli format.

    Args:
        key: Setting name (e.g. ipv4_method)

    Returns:
        nmcli setting name (e.g. ipv4.method)
    """
    if key.startswith(('ipv4_', 'ipv6_')):
        return key.replace('_', '.', 1)
    if key == 'interface_name':
        return 'connection.interface-name'
    if key == 'autoconnect':
        return 'connection.autoconnect'
    return key


@dataclass
class NetworkConnection:
    """NetworkManager connection representation.

    This class provides functionality for managing NetworkManager connections:
    - Connection configuration
    - Interface binding
    - Network settings

    Args:
        name: Connection name (optional, discovered from UUID)
        uuid: Connection UUID (optional, discovered from name)
        interface: Interface name (optional, discovered from connection)
        conn_type: Connection type (optional, defaults to ethernet)

    Example:
        ```python
        conn = NetworkConnection()  # Discovers first available connection
        conn = NetworkConnection(name='eth0')  # Discovers other values
        ```
    """

    # Optional parameters
    name: str | None = None
    uuid: str | None = None
    interface: str | None = None
    conn_type: ConnectionType = 'ethernet'

    def __post_init__(self) -> None:
        """Initialize connection.

        Discovers name, UUID, and interface if not provided.
        """
        # Discover connection info if needed
        if not self.name or not self.uuid:
            # Try by UUID first
            if self.uuid:
                result = run(f'nmcli -g connection.id,connection.interface-name conn show "{self.uuid}"')
                if result.succeeded:
                    with suppress(ValueError):
                        name, interface = result.stdout.splitlines()
                        self.name = name
                        self.interface = interface if interface != '--' else None

            # Try by name
            elif self.name:
                result = run(f'nmcli -g connection.uuid conn show "{self.name}"')
                if result.succeeded:
                    self.uuid = result.stdout.strip()
                    # Get interface
                    result = run(f'nmcli -g connection.interface-name conn show "{self.uuid}"')
                    if result.succeeded:
                        interface = result.stdout.strip()
                        self.interface = interface if interface != '--' else None

            # Try by interface
            elif self.interface:
                result = run(f'nmcli -g GENERAL.CONNECTION device show {self.interface}')
                if result.succeeded:
                    conn_name = result.stdout.strip()
                    if conn_name and conn_name != '--':
                        self.name = conn_name
                        # Get UUID
                        result = run(f'nmcli -g connection.uuid conn show "{self.name}"')
                        if result.succeeded:
                            self.uuid = result.stdout.strip()

    def exists(self) -> bool:
        """Check if connection exists.

        Returns:
            True if connection exists, False otherwise

        Example:
            ```python
            conn.exists()
            True
            ```
        """
        if not self.uuid and not self.name:
            return False

        if self.uuid:
            result = run(f'nmcli -g connection.uuid conn show "{self.uuid}"')
            return result.succeeded

        result = run(f'nmcli -g connection.uuid conn show "{self.name}"')
        return result.succeeded

    def up(self) -> bool:
        """Activate connection.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            conn.up()
            True
            ```
        """
        if not self.uuid and not self.name:
            logging.error('Connection UUID or name required')
            return False

        result = run(f'nmcli connection up "{self.uuid or self.name}"')
        return result.succeeded

    def down(self) -> bool:
        """Deactivate connection.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            conn.down()
            True
            ```
        """
        if not self.uuid and not self.name:
            logging.error('Connection UUID or name required')
            return False

        result = run(f'nmcli connection down "{self.uuid or self.name}"')
        return result.succeeded

    def delete(self) -> bool:
        """Delete connection.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            conn.delete()
            True
            ```
        """
        if not self.uuid and not self.name:
            logging.error('Connection UUID or name required')
            return False

        result = run(f'nmcli connection delete "{self.uuid or self.name}"')
        return result.succeeded

    def modify(self, setting: str, value: str) -> bool:
        """Modify connection setting.

        Args:
            setting: Setting to modify (e.g. ipv4.method)
            value: New value

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            conn.modify('ipv4.method', 'manual')
            True
            ```
        """
        if not self.uuid and not self.name:
            logging.error('Connection UUID or name required')
            return False

        result = run(f'nmcli connection modify "{self.uuid or self.name}" {setting} {value}')
        return result.succeeded

    def set_ip(self, ip: str, prefix: str | int = 24) -> bool:
        """Set IP address.

        Args:
            ip: IP address
            prefix: Network prefix (default: 24)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            conn.set_ip('192.168.1.100')
            True
            ```
        """
        try:
            addr = ipaddress.ip_address(ip)
            method = 'ipv4' if addr.version == IPV4_VERSION else 'ipv6'
        except ValueError:
            return False

        # Set manual method
        if not self.modify(f'{method}.method', 'manual'):
            return False

        # Set IP address
        if not self.modify(f'{method}.addresses', f'{ip}/{prefix}'):
            return False

        # Reactivate connection
        return self.up()


class NetworkManager:
    """NetworkManager operations.

    This class provides functionality for managing NetworkManager:
    - Connection management
    - Interface configuration
    - Network settings

    Example:
        ```python
        nm = NetworkManager()
        conn = nm.get_connection('eth0')
        conn.up()
        ```
    """

    def reload(self) -> bool:
        """Reload NetworkManager configuration.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            nm.reload()
            True
            ```
        """
        result = run('nmcli connection reload')
        return result.succeeded

    def get_connection(self, name_or_uuid: str | None = None) -> NetworkConnection | None:
        """Get connection by name or UUID.

        Args:
            name_or_uuid: Connection name or UUID (optional)

        Returns:
            NetworkConnection instance or None if not found

        Example:
            ```python
            nm.get_connection()  # Gets first available connection
            nm.get_connection('eth0')  # Gets specific connection
            ```
        """
        if not name_or_uuid:
            # Get first available connection
            result = run('nmcli -g connection.id,connection.uuid,connection.interface-name conn show')
            if result.succeeded and result.stdout:
                with suppress(ValueError):
                    name, uuid, interface = result.stdout.splitlines()[0].split(':')
                    return NetworkConnection(
                        name=name,
                        uuid=uuid,
                        interface=interface if interface != '--' else None,
                    )
            return None

        # Try by UUID first
        result = run(f'nmcli -g connection.id,connection.uuid,connection.interface-name conn show "{name_or_uuid}"')
        if result.succeeded:
            with suppress(ValueError):
                name, uuid, interface = result.stdout.splitlines()
                return NetworkConnection(
                    name=name,
                    uuid=uuid,
                    interface=interface if interface != '--' else None,
                )

        # Try by name
        result = run(f'nmcli -g connection.uuid conn show "{name_or_uuid}"')
        if result.succeeded:
            uuid = result.stdout.strip()
            return self.get_connection(uuid)

        return None

    def get_connection_by_interface(self, interface: str | NetworkInterface | None = None) -> NetworkConnection | None:
        """Get connection by interface.

        Args:
            interface: Interface name or NetworkInterface instance (optional)

        Returns:
            NetworkConnection instance or None if not found

        Example:
            ```python
            nm.get_connection_by_interface()  # Gets first available connection
            nm.get_connection_by_interface('eth0')  # Gets specific connection
            ```
        """
        if not interface:
            # Get first available interface
            result = run('nmcli -g GENERAL.DEVICE,GENERAL.CONNECTION device show')
            if result.succeeded and result.stdout:
                with suppress(ValueError):
                    device, conn_name = result.stdout.splitlines()[0].split(':')
                    if conn_name and conn_name != '--':
                        return self.get_connection(conn_name)
            return None

        name = interface.name if isinstance(interface, NetworkInterface) else interface
        result = run(f'nmcli -g GENERAL.CONNECTION device show {name}')
        if result.failed:
            return None

        conn_name = result.stdout.strip()
        if not conn_name or conn_name == '--':
            return None

        return self.get_connection(conn_name)

    def add_connection(
        self,
        name: str | None = None,
        interface: str | NetworkInterface | None = None,
        conn_type: ConnectionType = 'ethernet',
        **settings: str,
    ) -> NetworkConnection | None:
        """Add new connection.

        Args:
            name: Connection name (optional, defaults to interface name)
            interface: Interface name or NetworkInterface instance (optional)
            conn_type: Connection type (optional, defaults to ethernet)
            **settings: Additional settings (see ConnectionSettings)

        Returns:
            NetworkConnection instance or None if failed

        Example:
            ```python
            nm.add_connection()  # Creates connection with defaults
            nm.add_connection('eth0', interface='eth0')  # Creates specific connection
            ```
        """
        # Get interface name if provided
        ifname = None
        if interface:
            ifname = interface.name if isinstance(interface, NetworkInterface) else interface
            # Use interface name as connection name if not provided
            if not name:
                name = ifname

        # Generate connection name if not provided
        if not name:
            # Find first unused name
            i = 0
            while True:
                name = f'connection{i}'
                if not self.get_connection(name):
                    break
                i += 1

        # Build command
        cmd = ['nmcli', 'connection', 'add', 'type', conn_type, 'con-name', name]

        # Add interface if specified
        if ifname:
            cmd.extend(['ifname', ifname])

        # Add settings
        for key, value in settings.items():
            cmd.extend([_convert_setting_name(key), value])

        # Create connection
        result = run(' '.join(cmd))
        if result.failed:
            return None

        # Get new connection
        return self.get_connection(name)
