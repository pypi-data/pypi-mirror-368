# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSCSI device management.

This module provides functionality for managing iSCSI devices:
- Device discovery
- Device information
- Device operations

iSCSI (Internet SCSI) enables:
- Block storage over IP networks
- SAN functionality without FC hardware
- Storage consolidation and sharing
- Remote boot capabilities

Key concepts:
- Initiator: Client that accesses storage
- Target: Storage server that provides devices
- IQN: iSCSI Qualified Name (unique identifier)
- Portal: IP:Port where target listens
- Session: Connection between initiator and target
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from sts.utils.cmdline import run
from sts.utils.errors import DeviceError
from sts.utils.system import SystemManager

from .iscsiadm import IscsiAdm
from .session import IscsiSession

# Service name for systemd
ISCSID_SERVICE_NAME = 'iscsid'


@dataclass
class IscsiDevice:
    """iSCSI device representation.

    An iSCSI device represents a remote block device that:
    - Appears as a local SCSI device
    - Requires network connectivity
    - Can use authentication (CHAP)
    - Supports multipath for redundancy

    Args:
        name: Device name (e.g. 'sda')
        path: Device path (e.g. '/dev/sda')
        size: Device size in bytes
        ip: Target IP address
        port: Target port (default: 3260)
        target_iqn: Target IQN (e.g. 'iqn.2003-01.org.linux-iscsi.target')
        initiator_iqn: Initiator IQN (optional, from /etc/iscsi/initiatorname.iscsi)

    Example:
        ```python
        device = IscsiDevice(
            name='sda',
            path='/dev/sda',
            size=1000000000000,
            ip='192.168.1.100',
            target_iqn='iqn.2003-01.org.linux-iscsi.target',
        )
        ```
    """

    name: str
    path: Path | str
    size: int
    ip: str
    target_iqn: str
    port: int = 3260
    initiator_iqn: str | None = None

    # Internal fields
    _session_id: str | None = field(init=False, default=None)
    _iscsiadm: IscsiAdm = field(init=False, default_factory=IscsiAdm)

    # Important system paths
    ISCSI_PATH: ClassVar[Path] = Path('/sys/class/iscsi_session')  # Session info
    DATABASE_PATH: ClassVar[Path] = Path('/var/lib/iscsi')  # iSCSI database
    CONFIG_PATH: ClassVar[Path] = Path('/etc/iscsi')  # Configuration

    def __post_init__(self) -> None:
        """Initialize iSCSI device.

        Converts path string to Path object if needed.
        """
        # Convert path to Path if needed
        if isinstance(self.path, str):
            self.path = Path(self.path)

    @property
    def session_id(self) -> str | None:
        """Get iSCSI session ID.

        The session ID uniquely identifies an active connection:
        - Format is typically a small integer (e.g. '1')
        - None if device is not logged in
        - Cached to avoid repeated lookups

        Returns:
            Session ID if device is logged in, None otherwise

        Example:
            ```python
            device.session_id
            '1'
            ```
        """
        if self._session_id:
            return self._session_id

        # Try to find session ID by matching target and portal
        for session in IscsiSession.get_all():
            if session.target_iqn == self.target_iqn and session.portal.startswith(self.ip):
                self._session_id = session.session_id
                return self._session_id

        return None

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        """Set iSCSI session ID.

        Args:
            value: Session ID
        """
        self._session_id = value

    @session_id.deleter
    def session_id(self) -> None:
        """Delete iSCSI session ID.

        Clears cached session ID when session ends.
        """
        self._session_id = None

    def login(self) -> bool:
        """Log in to target.

        Login process:
        1. Discover target (SendTargets)
        2. Create session
        3. Authenticate if needed
        4. Create device nodes

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.login()
            True
            ```
        """
        if self.session_id:
            logging.info('Already logged in')
            return True

        # First discover the target using SendTargets
        result = self._iscsiadm.discovery(portal=f'{self.ip}:{self.port}')
        if result.failed:
            logging.error('Discovery failed')
            return False

        # Then login to create session
        result = self._iscsiadm.node_login(**{'-p': f'{self.ip}:{self.port}', '-T': self.target_iqn})
        if result.failed:
            logging.error('Login failed')
            return False

        return True

    def logout(self) -> bool:
        """Log out from target.

        Logout process:
        1. Close session
        2. Remove device nodes
        3. Clear session ID

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.logout()
            True
            ```
        """
        if not self.session_id:
            logging.info('Not logged in')
            return True

        result = self._iscsiadm.node_logout(**{'-p': f'{self.ip}:{self.port}', '-T': self.target_iqn})
        if result.failed:
            logging.error('Logout failed')
            return False

        self._session_id = None
        return True

    def _update_config_file(self, parameters: dict[str, str]) -> bool:
        """Update iscsid.conf with parameters.

        Updates configuration while preserving:
        - Comments and formatting
        - Existing settings
        - File permissions

        Args:
            parameters: Parameters to update

        Returns:
            True if successful, False otherwise
        """
        config_path = self.CONFIG_PATH / 'iscsid.conf'
        try:
            # Read existing config
            with config_path.open('r') as f:
                lines = f.readlines()

            # Update or add parameters
            for key, value in parameters.items():
                found = False
                for i, line in enumerate(lines):
                    if line.strip().startswith('#'):
                        continue
                    if '=' in line:
                        file_key = line.split('=', 1)[0].strip()
                        if file_key == key:
                            lines[i] = f'{key} = {value}\n'
                            found = True
                            break
                if not found:
                    lines.append(f'{key} = {value}\n')

            # Write updated config
            with config_path.open('w') as f:
                f.writelines(lines)
        except OSError:
            logging.exception('Failed to update config file')
            return False

        return True

    def _restart_service(self) -> bool:
        """Restart iscsid service.

        Required after configuration changes:
        - Reloads configuration
        - Maintains existing sessions
        - Updates authentication

        Returns:
            True if successful, False otherwise
        """
        return SystemManager().service_restart(ISCSID_SERVICE_NAME)

    def set_chap(
        self,
        username: str,
        password: str,
        mutual_username: str | None = None,
        mutual_password: str | None = None,
    ) -> bool:
        """Set CHAP authentication.

        CHAP (Challenge Handshake Authentication Protocol):
        - One-way: Target authenticates initiator
        - Mutual: Both sides authenticate each other
        - Requires matching config on target

        Args:
            username: CHAP username
            password: CHAP password
            mutual_username: Mutual CHAP username (optional)
            mutual_password: Mutual CHAP password (optional)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.set_chap('user', 'pass')
            True
            ```
        """
        if not username or not password:
            logging.error('Username and password required')
            return False

        # Build parameters for both node and discovery
        parameters = {
            'node.session.auth.authmethod': 'CHAP',
            'node.session.auth.username': username,
            'node.session.auth.password': password,
            'discovery.sendtargets.auth.authmethod': 'CHAP',
            'discovery.sendtargets.auth.username': username,
            'discovery.sendtargets.auth.password': password,
        }

        # Add mutual CHAP if provided
        if mutual_username and mutual_password:
            parameters.update(
                {
                    'node.session.auth.username_in': mutual_username,
                    'node.session.auth.password_in': mutual_password,
                    'discovery.sendtargets.auth.username_in': mutual_username,
                    'discovery.sendtargets.auth.password_in': mutual_password,
                }
            )

        # Update config and restart service
        return self._update_config_file(parameters) and self._restart_service()

    def disable_chap(self) -> bool:
        """Disable CHAP authentication.

        Removes all CHAP settings:
        - Node authentication
        - Discovery authentication
        - Mutual CHAP settings

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.disable_chap()
            True
            ```
        """
        config_path = self.CONFIG_PATH / 'iscsid.conf'
        try:
            # Read existing config
            with config_path.open('r') as f:
                lines = f.readlines()

            # Keep only non-CHAP lines
            new_lines = [
                line
                for line in lines
                if not any(
                    p in line
                    for p in (
                        'node.session.auth.',
                        'discovery.sendtargets.auth.',
                    )
                )
                or line.strip().startswith('#')
            ]

            # Write updated config
            with config_path.open('w') as f:
                f.writelines(new_lines)
        except OSError:
            logging.exception('Failed to update config file')
            return False

        return self._restart_service()

    @classmethod
    def _parse_device_info(cls, info: dict[str, str]) -> IscsiDevice | None:
        """Parse device info into IscsiDevice instance.

        Creates device object from dictionary:
        - Validates required fields
        - Converts types as needed
        - Handles missing fields

        Args:
            info: Device info dictionary

        Returns:
            IscsiDevice instance or None if parsing failed
        """
        try:
            return cls(
                name=info['name'],
                path=f'/dev/{info["name"]}',
                size=int(info['size']),
                ip=info['ip'],
                port=int(info['port']),
                target_iqn=info['target_iqn'],
            )
        except (KeyError, ValueError, DeviceError):
            logging.warning('Failed to create device')
            return None

    @classmethod
    def get_all(cls) -> list[IscsiDevice]:
        """Get list of all iSCSI devices.

        Discovery process:
        1. Get all active sessions
        2. Get portal info for each session
        3. Get disk info for each session
        4. Create device objects

        Returns:
            List of IscsiDevice instances

        Example:
            ```python
            IscsiDevice.get_all()
            [IscsiDevice(name='sda', ...), IscsiDevice(name='sdb', ...)]
            ```
        """
        devices = []
        for session in IscsiSession.get_all():
            # Get session details
            session_data = session.get_data_p2()
            if not session_data:
                continue

            # Get portal info (IP:Port)
            portal = session_data.get('Current Portal', '').split(',')[0]
            if not portal:
                continue
            ip, port = portal.split(':')

            # Get disks associated with session
            for disk in session.get_disks():
                if not disk.is_running():
                    continue

                # Get disk size using blockdev
                try:
                    result = run(f'blockdev --getsize64 /dev/{disk.name}')
                    if result.failed:
                        continue
                    size = int(result.stdout)
                except (ValueError, DeviceError):
                    continue

                # Create device object
                device = cls(
                    name=disk.name,
                    path=f'/dev/{disk.name}',
                    size=size,
                    ip=ip,
                    port=int(port),
                    target_iqn=session.target_iqn,
                )
                devices.append(device)

        return devices

    @classmethod
    def discover(cls, ip: str, port: int = 3260) -> list[str]:
        """Discover available targets.

        Uses SendTargets discovery:
        - Queries portal for targets
        - Returns list of IQNs
        - No authentication needed
        - Fast operation

        Args:
            ip: Target IP address
            port: Target port (default: 3260)

        Returns:
            List of discovered target IQNs

        Example:
            ```python
            IscsiDevice.discover('192.168.1.100')
            ['iqn.2003-01.org.linux-iscsi.target1', 'iqn.2003-01.org.linux-iscsi.target2']
            ```
        """
        iscsiadm = IscsiAdm()
        result = iscsiadm.discovery(portal=f'{ip}:{port}')
        if result.failed:
            logging.warning('No targets found')
            return []

        targets = []
        for line in result.stdout.splitlines():
            # Parse line like: 192.168.1.100:3260,1 iqn.2003-01.target
            parts = line.split()
            if len(parts) > 1 and parts[-1].startswith('iqn.'):
                targets.append(parts[-1])

        return targets
