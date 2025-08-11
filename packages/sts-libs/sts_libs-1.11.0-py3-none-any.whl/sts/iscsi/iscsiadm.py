# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSCSI admin interface.

This module provides a wrapper for the iscsiadm command line tool:
- Command building
- Debug level control

iscsiadm is the main configuration tool for:
- iSCSI initiator configuration
- Session management
- Discovery operations
- Interface configuration
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar, Final, Literal

from sts.utils.cmdline import CommandResult, run
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from collections.abc import Mapping

# Command and package names
CLI_NAME: Final[str] = 'iscsiadm'  # Command name
PACKAGE_NAME: Final[str] = 'iscsi-initiator-utils'  # Package providing iscsiadm


class IscsiAdm:
    """Wrapper for iscsiadm command line tool.

    iscsiadm operates in different modes:
    - discovery: Find available targets
    - node: Manage target nodes
    - session: Handle active sessions
    - iface: Configure network interfaces
    - fw: Firmware operations

    Args:
        debug_level: Print iscsiadm debug info (0-8)
            0: No debug
            1: Error
            2: Warning
            3: Info
            4: Debug
            5-8: Protocol details
    """

    def __init__(
        self,
        debug_level: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] = 0,
    ) -> None:
        """Initialize the IscsiAdm instance.

        Args:
            debug_level (Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]): Print iscsiadm debug info (0-8).
        """
        self.debug_level = debug_level

        # Ensure package is installed
        system = SystemManager()
        if not system.package_manager.install(PACKAGE_NAME):
            logging.critical(f'Could not install {PACKAGE_NAME}')
        # /etc/iscsi/initiatorname.iscsi is generated during starting iscsid service
        if not system.service_start('iscsid'):
            logging.critical('Could not start iscsid')

    # Mode-specific options from iscsiadm.c
    # Each mode supports a subset of options
    MODES: ClassVar[Mapping[str, str]] = {
        'discovery': 'DSIPdntplov',  # Discovery operations
        'discoverydb': 'DSIPdntplov',  # Discovery database
        'node': 'RsPIdlSonvupTULW',  # Node operations
        'session': 'PiRdrusonuSv',  # Session operations
        'host': 'CHdPotnvxA',  # Host operations
        'iface': 'HIdnvPoCabci',  # Interface operations
        'fw': 'dlWnv',  # Firmware operations
    }

    # Mapping between short and long option forms
    # Short forms are single letters, long forms are descriptive
    OPTIONS: ClassVar[Mapping[str, str]] = {
        'p': 'portal',  # Portal address
        'T': 'targetname',  # Target name (IQN)
        'I': 'interface',  # Interface name
        'o': 'op',  # Operation
        't': 'type',  # Type (e.g. sendtargets)
        'n': 'name',  # Name
        'v': 'value',  # Value
        'H': 'host',  # Host number
        'r': 'sid',  # Session ID
        'R': 'rescan',  # Rescan for changes
        'P': 'print',  # Print information
        'D': 'discover',  # Discover targets
        'l': 'login',  # Login to target
        'L': 'loginall',  # Login to all targets
        'u': 'logout',  # Logout from target
        'U': 'logoutall',  # Logout from all targets
        's': 'stats',  # Show statistics
        'k': 'killiscsid',  # Kill iscsid daemon
        'd': 'debug',  # Debug level
        'S': 'show',  # Show information
        'V': 'version',  # Show version
        'h': 'help',  # Show help
        'C': 'submode',  # Submode
        'a': 'ip',  # IP address
        'b': 'packetsize',  # Packet size
        'c': 'count',  # Count
        'i': 'interval',  # Interval
        'x': 'index',  # Index
        'A': 'portal_type',  # Portal type
        'W': 'no_wait',  # Don't wait for completion
    }

    def get_short_options_list(self, mode: str) -> list[str]:
        """Get list of short options for mode.

        Each mode supports a specific set of short options.
        This method returns the valid options for a mode.

        Args:
            mode: iscsiadm mode (e.g. 'node', 'session')

        Returns:
            List of short options (e.g. ['l', 'u', 'T'])

        Raises:
            ValueError: If mode is invalid
        """
        if mode not in self.MODES:
            raise ValueError(f'Invalid mode: {mode}')
        return [*self.MODES[mode]]

    def get_long_options_list(self, mode: str) -> list[str]:
        """Get list of long options for mode.

        Converts short options to their long forms:
        - More readable
        - Self-documenting
        - Same functionality

        Args:
            mode: iscsiadm mode (e.g. 'node', 'session')

        Returns:
            List of long options (e.g. ['login', 'logout', 'targetname'])

        Raises:
            ValueError: If mode is invalid
        """
        if mode not in self.MODES:
            raise ValueError(f'Invalid mode: {mode}')
        return [self.OPTIONS[short_option] for short_option in self.get_short_options_list(mode)]

    def available_options(self, mode: str) -> list[str]:
        """Get list of all available options for mode.

        Returns both short and long forms:
        - Allows flexible usage
        - Complete reference
        - Validation helper

        Args:
            mode: iscsiadm mode (e.g. 'node', 'session')

        Returns:
            List of all options (short and long forms)
        """
        return self.get_short_options_list(mode) + self.get_long_options_list(mode)

    def _run(
        self,
        mode: str = '',
        arguments: Mapping[str, str | None] | None = None,
    ) -> CommandResult:
        """Run iscsiadm command.

        Builds and executes command with:
        - Specified mode
        - Given arguments
        - Debug level if set

        Args:
            mode: iscsiadm mode (e.g. 'node', 'session')
            arguments: Dictionary of arguments

        Returns:
            CommandResult instance
        """
        command_list: list[str] = [CLI_NAME, '--mode', mode]
        if arguments is not None:
            # Only include arguments that have values or are flags
            command_list.extend(
                f'{k} {v}' if v is not None else k for k, v in arguments.items() if v is not None or k.startswith('--')
            )
        if self.debug_level:
            command_list += ['--debug', str(self.debug_level)]
        command: str = ' '.join(command_list)
        return run(command)

    def iface(
        self,
        op: str,
        iface: str,
        name: str | None = None,
        value: str | None = None,
    ) -> CommandResult:
        """Run iscsiadm iface command.

        Interface operations:
        - new: Create interface
        - delete: Remove interface
        - update: Modify parameters
        - show: Display configuration

        Args:
            op: Operation (new, delete, update)
            iface: Interface name
            name: Parameter name
            value: Parameter value

        Returns:
            CommandResult instance
        """
        arguments: dict[str, str | None] = {'-o': op, '-I': iface}
        if name is not None:
            arguments['-n'] = name
        if value is not None:
            arguments['-v'] = value
        return self._run(mode='iface', arguments=arguments)

    def iface_update(self, iface: str, name: str, value: str) -> CommandResult:
        """Update iSCSI interface parameter.

        Common parameters:
        - iface.initiatorname: Local IQN
        - iface.ipaddress: Local IP
        - iface.hwaddress: MAC address
        - iface.transport_name: Transport type

        Args:
            iface: Interface name
            name: Parameter name
            value: Parameter value

        Returns:
            CommandResult instance
        """
        return self.iface(op='update', iface=iface, name=f'iface.{name}', value=value)

    def iface_update_iqn(self, iface: str, iqn: str) -> CommandResult:
        """Update iSCSI interface initiator name.

        Sets local IQN for interface:
        - Must be valid IQN format
        - Must be unique on network
        - Used for authentication

        Args:
            iface: Interface name
            iqn: Initiator IQN

        Returns:
            CommandResult instance
        """
        return self.iface_update(iface=iface, name='initiatorname', value=iqn)

    def iface_update_ip(self, iface: str, ip: str) -> CommandResult:
        """Update iSCSI interface IP address.

        Sets local IP for interface:
        - Must be reachable
        - Can be IPv4 or IPv6
        - Used for connections

        Args:
            iface: Interface name
            ip: IP address

        Returns:
            CommandResult instance
        """
        return self.iface_update(iface=iface, name='ipaddress', value=ip)

    def iface_exists(self, iface: str) -> bool:
        """Check if iSCSI interface exists.

        Args:
            iface: Interface name

        Returns:
            True if interface exists
        """
        return self.iface(op='show', iface=iface).succeeded

    def discovery(
        self,
        portal: str = '127.0.0.1',
        type: str = 'st',  # noqa: A002
        interface: str | None = None,
        **kwargs: str,
    ) -> CommandResult:
        """Run iscsiadm discovery command.

        Discovery types:
        - st: SendTargets (most common)
        - isns: iSNS server
        - fw: Firmware
        - slp: Service Location Protocol

        Args:
            portal: Portal address (IP:Port)
            type: Discovery type (st, isns, fw, slp)
            interface: Interface name
            **kwargs: Additional arguments

        Returns:
            CommandResult instance
        """
        arguments: dict[str, str | None] = {'-t': type, '-p': portal}
        if kwargs:
            arguments.update(kwargs)
        if interface:
            arguments['-I'] = interface
        return self._run(mode='discovery', arguments=arguments)

    def node(self, **kwargs: str | None) -> CommandResult:
        """Run iscsiadm node command.

        Node operations:
        - Login/logout
        - Update parameters
        - Show information
        - Delete node

        Args:
            **kwargs: Arguments

        Returns:
            CommandResult instance
        """
        return self._run(mode='node', arguments=kwargs)

    def node_login(self, **kwargs: str) -> CommandResult:
        """Run iscsiadm node login command.

        Login process:
        1. Create new session
        2. Authenticate if needed
        3. Create SCSI devices

        Args:
            **kwargs: Arguments

        Returns:
            CommandResult instance
        """
        arguments: dict[str, str | None] = {'--login': None}
        arguments.update(kwargs)
        return self.node(**arguments)

    def node_logout(self, **kwargs: str) -> CommandResult:
        """Run iscsiadm node logout command.

        Logout process:
        1. Remove SCSI devices
        2. Close session
        3. Cleanup resources

        Args:
            **kwargs: Arguments

        Returns:
            CommandResult instance
        """
        arguments: dict[str, str | None] = {'--logout': None}
        arguments.update(kwargs)
        return self.node(**arguments)

    def node_logoutall(self, how: Literal['all', 'manual', 'automatic', 'onboot'] = 'all') -> CommandResult:
        """Run iscsiadm node logoutall command.

        Logout types:
        - all: All sessions except boot nodes
        - manual: Manually created sessions
        - automatic: Automatically created sessions
        - onboot: Boot sessions

        Args:
            how: Logout type (all, manual, automatic, onboot)

        Returns:
            CommandResult instance

        Note:
            Use 'all' to log out of all sessions except boot nodes
        """
        arguments: dict[str, str | None] = {'--logoutall': how}
        return self.node(**arguments)

    def session(self, **kwargs: str | None) -> CommandResult:
        """Run iscsiadm session command.

        Session operations:
        - List active sessions
        - Show session details
        - Rescan for devices
        - Show statistics

        Args:
            **kwargs: Arguments

        Returns:
            CommandResult instance
        """
        return self._run(mode='session', arguments=kwargs)
