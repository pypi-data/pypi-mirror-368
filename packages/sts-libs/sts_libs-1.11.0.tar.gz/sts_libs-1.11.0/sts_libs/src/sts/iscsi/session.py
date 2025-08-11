# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSCSI session management.

This module provides functionality for managing iSCSI sessions:
- Session discovery
- Session information
- Session operations

An iSCSI session represents:
- Connection between initiator and target
- Authentication and parameters
- Associated SCSI devices
- Network transport details
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from .iscsiadm import IscsiAdm
from .parameters import PARAM_MAP


@dataclass
class IscsiSession:
    """iSCSI session representation.

    A session maintains the connection state between:
    - Initiator (local system)
    - Target (remote storage)
    - Multiple connections possible
    - Negotiated parameters

    Args:
        session_id: Session ID (unique identifier)
        target_iqn: Target IQN (iSCSI Qualified Name)
        portal: Portal address (IP:Port)
    """

    session_id: str
    target_iqn: str
    portal: str
    _iscsiadm: IscsiAdm = field(init=False, default_factory=IscsiAdm)

    def logout(self) -> bool:
        """Log out from session.

        Logout process:
        - Closes all connections
        - Removes session
        - Cleans up resources

        Returns:
            True if successful, False otherwise
        """
        result = self._iscsiadm.node_logout(
            **{'-p': self.portal, '-T': self.target_iqn},
        )
        if result.failed:
            logging.error('Logout failed')
            return False
        return True

    def get_data(self) -> dict[str, str]:
        """Get session data.

        Retrieves basic session information:
        - Authentication method
        - CHAP credentials
        - Connection parameters
        - Session options

        Returns:
            Dictionary of session data from 'iscsiadm -m session -r <sid> -S'

        Example:
            ```python
            session.get_data()
            {
                'node.session.auth.authmethod': 'None',
                'node.session.auth.username': '',
                'node.session.auth.password': '',
                ...
            }
            ```
        """
        result = self._iscsiadm.session(**{'-r': self.session_id, '-S': None})
        if result.failed:
            return {}

        # Parse key=value pairs, skipping comments
        data = {}
        lines = [line for line in result.stdout.splitlines() if line and not line.startswith('#')]
        for line in lines:
            key_val = line.split(' = ', 1)
            if len(key_val) == 2:
                data[key_val[0]] = key_val[1]
        return data

    def get_data_p2(self) -> dict[str, str]:
        """Get session data with print level 2.

        Retrieves detailed session information:
        - Target details
        - Portal information
        - Connection state
        - SCSI information

        Returns:
            Dictionary of session data from 'iscsiadm -m session -r <sid> -S -P 2'

        Example:
            ```python
            session.get_data_p2()
            {
                'Target': 'iqn.2003-01.org.linux-iscsi.target',
                'Current Portal': '192.168.1.100:3260,1',
                'Persistent Portal': '192.168.1.100:3260',
                ...
            }
            ```
        """
        result = self._iscsiadm.session(**{'-r': self.session_id, '-S': None, '-P': '2'})
        if result.failed:
            return {}

        # Parse key: value pairs, removing tabs
        data = {}
        lines = [line.replace('\t', '') for line in result.stdout.splitlines() if line and ': ' in line]
        for line in lines:
            key_val = line.split(': ', 1)
            if len(key_val) == 2:
                data[key_val[0]] = key_val[1]
        return data

    @dataclass
    class SessionDisk:
        """iSCSI session disk representation.

        Represents a SCSI disk exposed through the session:
        - Maps to local block device
        - Has SCSI addressing (H:C:T:L)
        - Tracks operational state

        Attributes:
            name: Disk name (e.g. 'sda')
            state: Disk state (e.g. 'running')
            scsi_n: SCSI host number
            channel: SCSI channel number
            id: SCSI target ID
            lun: SCSI Logical Unit Number
        """

        name: str
        state: str
        scsi_n: str
        channel: str
        id: str
        lun: str

        def is_running(self) -> bool:
            """Check if disk is running.

            'running' state indicates:
            - Device is accessible
            - I/O is possible
            - No error conditions

            Returns:
                True if disk state is 'running'
            """
            return self.state == 'running'

    def get_disks(self) -> list[SessionDisk]:
        """Get list of disks attached to session.

        Discovers SCSI disks by:
        - Parsing session information
        - Matching SCSI addresses
        - Checking device states

        Returns:
            List of SessionDisk instances

        Example:
            ```python
            session.get_disks()
            [SessionDisk(name='sda', state='running', scsi_n='2', channel='00', id='0', lun='0')]
            ```
        """
        result = self._iscsiadm.session(**{'-r': self.session_id, '-P': '3'})
        if result.failed or 'Attached scsi disk' not in result.stdout:
            return []

        disks = []
        # Match SCSI info lines like: "scsi2 Channel 00 Id 0 Lun: 0"
        scsi_pattern = r'scsi(\d+)\s+Channel\s+(\d+)\s+Id\s+(\d+)\s+Lun:\s+(\d+)'
        # Match disk info lines like: "Attached scsi disk sda State: running"
        disk_pattern = r'Attached\s+scsi\s+disk\s+(\w+)\s+State:\s+(\w+)'

        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            # First find SCSI address
            scsi_match = re.search(scsi_pattern, line)
            if not scsi_match:
                continue

            # Then look for disk info in next line
            if i + 1 >= len(lines):
                continue

            disk_match = re.search(disk_pattern, lines[i + 1])
            if not disk_match:
                continue

            # Create disk object with all information
            disks.append(
                self.SessionDisk(
                    name=disk_match.group(1),  # Device name (e.g. sda)
                    state=disk_match.group(2),  # Device state
                    scsi_n=scsi_match.group(1),  # Host number
                    channel=scsi_match.group(2),  # Channel number
                    id=scsi_match.group(3),  # Target ID
                    lun=scsi_match.group(4),  # LUN
                ),
            )

        return disks

    @classmethod
    def get_all(cls) -> list[IscsiSession]:
        """Get list of all iSCSI sessions.

        Lists active sessions by:
        - Querying iscsiadm
        - Parsing session information
        - Creating session objects

        Returns:
            List of IscsiSession instances
        """
        iscsiadm = IscsiAdm()
        result = iscsiadm.session()
        if result.failed:
            return []

        sessions = []
        for line in result.stdout.splitlines():
            # Parse line like:
            # tcp: [1] 192.168.1.100:3260,1 iqn.2003-01.target
            if not line:
                continue
            parts = line.split()
            if len(parts) < 4:  # Need at least tcp: [id] portal target
                continue
            session_id = parts[1].strip('[]')
            portal = parts[2].split(',')[0]  # Remove portal group tag
            target_iqn = parts[3]
            sessions.append(cls(session_id=session_id, target_iqn=target_iqn, portal=portal))

        return sessions

    @classmethod
    def get_by_target(cls, target_iqn: str) -> list[IscsiSession]:
        """Get session by target IQN.

        Finds session matching target:
        - Searches all active sessions
        - Matches exact IQN
        - Returns all matches

        Args:
            target_iqn: Target IQN

        Returns:
            List of IscsiSession instances matching target IQN
        """
        return [session for session in cls.get_all() if session.target_iqn == target_iqn]

    @classmethod
    def get_by_portal(cls, portal: str) -> list[IscsiSession]:
        """Get session by portal address.

        Finds session matching portal:
        - Searches all active sessions
        - Matches exact portal address
        - Returns first match

        Args:
            portal: Portal address (e.g. '127.0.0.1:3260')

        Returns:
            List of IscsiSession instances matching portal
        """
        return [session for session in cls.get_all() if session.portal == portal]

    def get_parameters(self) -> dict[str, str]:
        """Get parameters from session.

        Retrieves negotiated parameters:
        - Connection settings
        - Authentication options
        - Performance tuning
        - Error recovery

        Returns:
            Dictionary of parameters
        """
        # Get parameters from session data
        data = self.get_data_p2()
        if not data:
            logging.warning('Failed to get session data')
            return {}

        # Extract negotiated parameters
        negotiated = {}
        for param_name in PARAM_MAP:
            if param_name not in data:
                logging.warning(f'Parameter {param_name} not found in session data')
                continue
            negotiated[param_name] = data[param_name]

        return negotiated
