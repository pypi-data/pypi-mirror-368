# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSCSI configuration.

This module provides configuration classes for iSCSI:
- Interface configuration
- Node configuration
- Overall configuration
- Daemon configuration

Key components:
- Initiator name (unique identifier)
- Network interfaces
- Target discovery
- Authentication
- Service management
"""

from __future__ import annotations

import logging
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

from sts.utils.config import Config
from sts.utils.string_extras import rand_string
from sts.utils.system import SystemManager

from .iscsiadm import IscsiAdm

# Service names for systemd
ISCSID_SERVICE_NAME = 'iscsid'  # Main iSCSI daemon
ISCSIUIO_SERVICE_NAME = 'iscsiuio'  # User-space I/O daemon

# Characters allowed in iSCSI names per RFC 7143 Section 6.1
ISCSI_ALLOWED_CHARS = string.ascii_letters + string.digits + '.-+@_=:/[],~'


def rand_iscsi_string(length: int) -> str | None:
    """Generate random string following iSCSI naming rules.

    Text format is based on Internet Small Computer System Interface (iSCSI) Protocol
    (RFC 7143) Section 6.1:
    - ASCII letters and digits
    - Limited punctuation
    - No spaces or control chars

    Args:
        length: Length of the random string

    Returns:
        Random string or None if length is invalid

    Example:
        ```python
        rand_iscsi_string(8)
        'Abc123_+'
        ```
    """
    return rand_string(length, chars=ISCSI_ALLOWED_CHARS)


def set_initiatorname(name: str) -> bool:
    """Set initiator name.

    The initiator name uniquely identifies this system:
    - Must be valid IQN format
    - Must be unique on network
    - Stored in /etc/iscsi/initiatorname.iscsi

    Args:
        name: Initiator name (IQN format)

    Returns:
        True if successful, False otherwise
    """
    system = SystemManager()
    try:
        Path('/etc/iscsi/initiatorname.iscsi').write_text(f'InitiatorName={name}\n')
        system.service_restart(ISCSID_SERVICE_NAME)
    except OSError:
        logging.exception('Failed to set initiator name')
        return False
    return True


def create_iscsi_iface(iface_name: str) -> bool:
    """Create iSCSI interface.

    An iSCSI interface binds sessions to:
    - Network interface
    - IP address
    - Hardware address
    - Transport type

    Args:
        iface_name: Interface name

    Returns:
        True if successful, False otherwise
    """
    iscsiadm = IscsiAdm()
    result = iscsiadm.iface(op='new', iface=iface_name)
    if result.failed:
        logging.error('Failed to create interface')
        return False
    return True


@dataclass
class IscsiInterface:
    """iSCSI interface configuration.

    An interface defines how iSCSI traffic is sent:
    - Which network interface to use
    - What IP address to bind to
    - Optional hardware address binding

    Attributes:
        iscsi_ifacename: Interface name (e.g. 'iface0')
        ipaddress: IP address to bind to
        hwaddress: Hardware address (optional, for HBA binding)
    """

    iscsi_ifacename: str
    ipaddress: str
    hwaddress: str | None = None


@dataclass
class IscsiNode:
    """iSCSI node configuration.

    A node represents a connection to a target:
    - Target identification
    - Network location
    - Interface binding
    - Session management

    Attributes:
        target_iqn: Target IQN (unique identifier)
        portal: Portal address (IP:Port)
        interface: Interface name to use
    """

    target_iqn: str
    portal: str
    interface: str
    iscsiadm: IscsiAdm = field(init=False, default_factory=IscsiAdm)

    def login(self) -> bool:
        """Log in to target.

        Login process:
        1. Discover target if needed
        2. Create new session
        3. Authenticate if configured
        4. Create SCSI devices

        Returns:
            True if successful, False otherwise
        """
        # First discover the target
        result = self.iscsiadm.discovery(portal=self.portal)
        if result.failed:
            logging.error('Discovery failed')
            return False

        # Then login to create session
        result = self.iscsiadm.node_login(**{'-p': self.portal, '-T': self.target_iqn})
        if result.failed:
            logging.error('Login failed')
            return False
        return True

    def logout(self) -> bool:
        """Log out from target.

        Logout process:
        1. Close session
        2. Remove SCSI devices
        3. Clean up resources

        Returns:
            True if successful, False otherwise
        """
        result = self.iscsiadm.node_logout(**{'-p': self.portal, '-T': self.target_iqn})
        if result.failed:
            logging.error('Logout failed')
            return False
        return True

    @classmethod
    def setup_and_login(cls, portal: str, initiator_iqn: str, target_iqn: str | None = None) -> IscsiNode:
        """Set up node and log in.

        Complete setup process:
        1. Create node configuration
        2. Discover target if needed
        3. Log in to create session

        Args:
            portal: Portal address (IP:Port)
            initiator_iqn: Initiator IQN (local identifier)
            target_iqn: Target IQN (optional, will be discovered)

        Returns:
            IscsiNode instance
        """
        # Create node with known info
        node = cls(
            target_iqn=target_iqn or '',  # Will be discovered if not provided
            portal=portal,
            interface=initiator_iqn,
        )

        # Discover target if IQN not provided
        if not target_iqn:
            result = node.iscsiadm.discovery(portal=portal)
            if result.succeeded:
                for line in result.stdout.splitlines():
                    if line.strip():  # Skip empty lines
                        # Format: portal target_iqn
                        # Example: 192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target1
                        parts = line.split()
                        if len(parts) >= 2:
                            node.target_iqn = parts[1]
                            break

        # Log in if we have target IQN
        if node.target_iqn:
            node.login()

        return node


class ConfVars(TypedDict):
    """iSCSI configuration variables.

    Complete configuration includes:
    - Local initiator name
    - List of targets to connect to
    - Network interface configurations
    - Hardware offload driver (if used)
    """

    initiatorname: str  # iqn.1994-05.redhat:example
    targets: list[IscsiNode]  # Target configurations
    ifaces: list[IscsiInterface]  # Interface configurations
    driver: str | None  # Hardware offload driver (e.g. 'bnx2i', 'qedi', 'cxgb4i')


@dataclass
class IscsiConfig:
    """iSCSI configuration.

    Complete iSCSI initiator configuration:
    - Local identification
    - Network setup
    - Target connections
    - Hardware offload

    Attributes:
        initiatorname: Initiator IQN (local identifier)
        ifaces: List of interface configurations
        targets: List of target configurations
        driver: Hardware offload driver name (if used)
    """

    initiatorname: str | None
    ifaces: list[IscsiInterface]
    targets: list[IscsiNode] | None
    driver: str | None


class IscsidConfig(Config):
    """iSCSI daemon configuration.

    Manages iscsid.conf settings:
    - Connection parameters
    - Authentication
    - Timeouts
    - Retry behavior
    """

    CONFIG_PATH = Path('/etc/iscsi/iscsid.conf')

    def __init__(self) -> None:
        """Initializes the class instance and loads the configuration file."""
        super().__init__(self.CONFIG_PATH)


def setup(variables: IscsiConfig) -> bool:
    """Configure iSCSI initiator based on env variables.

    Complete setup process:
    1. Set initiator name
    2. Configure interfaces
    3. Start required services
    4. Discover targets
    5. Enable services

    Args:
        variables: Configuration variables

    Returns:
        True if successful, False otherwise
    """
    iscsiadm = IscsiAdm()
    system = SystemManager()

    # Set initiator name
    if variables.initiatorname and not set_initiatorname(variables.initiatorname):
        return False

    # Set up network interfaces
    if variables.ifaces:
        for iface in variables.ifaces:
            ifacename = iface.iscsi_ifacename
            # Enable iscsiuio for hardware offload
            if variables.driver in {'qedi', 'bnx2i'} and not system.is_service_running(ISCSIUIO_SERVICE_NAME):
                if not system.service_enable(ISCSIUIO_SERVICE_NAME):
                    return False
                if not system.service_start(ISCSIUIO_SERVICE_NAME):
                    return False

            # Create interface if needed
            if not iscsiadm.iface_exists(iface=ifacename) and not create_iscsi_iface(iface_name=ifacename):
                return False

            # Update interface parameters
            result = iscsiadm.iface_update(iface=ifacename, name='ipaddress', value=iface.ipaddress)
            if result.failed:
                logging.error(f'Failed to update interface: {result.stderr}')
                return False

            if iface.hwaddress:
                result = iscsiadm.iface_update(iface=ifacename, name='hwaddress', value=iface.hwaddress)
                if result.failed:
                    logging.error(f'Failed to update interface: {result.stderr}')
                    return False

    # Discover configured targets
    if variables.targets:
        for target in variables.targets:
            if not iscsiadm.discovery(
                portal=target.portal, interface=target.interface, target_iqn=target.target_iqn
            ).succeeded:
                return False

    # Enable iscsid service for automatic startup
    if not system.is_service_enabled(ISCSID_SERVICE_NAME):
        return system.service_enable(ISCSID_SERVICE_NAME)
    return True
