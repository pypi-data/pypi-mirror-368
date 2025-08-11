# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Module to manipulate LIO target (using targetcli).

This module provides functionality for managing Linux-IO (LIO) targets:
- Backstore management (block, fileio, ramdisk)
- iSCSI target configuration
- Authentication and access control
- Portal and TPG management

LIO Target Components:
1. Backstores: Storage objects that provide data
   - fileio: File-backed storage
   - block: Block device storage
   - ramdisk: Memory-based storage
   - pscsi: Pass-through SCSI devices

2. Fabric Modules:
   - iSCSI: IP-based SCSI transport
   - FC: Fibre Channel transport
   - SRP: RDMA-based SCSI transport

3. Access Control:
   - TPGs: Target Portal Groups
   - ACLs: Access Control Lists
   - Authentication: CHAP and mutual CHAP
"""

from __future__ import annotations

import logging
import re
from contextlib import contextmanager
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from sts.blockdevice import BlockDevice, get_free_disks
from sts.utils import packages
from sts.utils.cmdline import run

if TYPE_CHECKING:
    from collections.abc import Generator

    from testinfra.backend.base import CommandResult

regex_tgtcli_wwpn = 'naa.\\S+'

TARGETCLI = 'targetcli'


class Targetcli:
    """Use to run targetcli commands.

    rtslib-fb API would normally be used in Python, however we want to test targetcli commands.

    Args:
        path: The path within targetcli shell structure
    """

    def __init__(self, path: str) -> None:
        """Initialize the Targetcli instance.

        Args:
            path: The path within targetcli shell structure
        """
        self.path = path
        pm = packages.Dnf()
        if not pm.install(TARGETCLI):
            logging.critical('Could not install targetcli package')

    def _run(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Execute a targetcli command.

        Args:
            *args: Positional arguments for the command
            **kwargs: Keyword arguments that will be converted to key=value pairs

        Returns:
            CommandResult from running the command
        """
        cmd = f'{TARGETCLI} {self.path} {" ".join(args)}'  # type: ignore [arg-type]
        arguments = {**kwargs}
        if arguments:
            arguments_unpacked = ' '.join([f'{key}={value}' for key, value in arguments.items()])
            cmd = f'{cmd} {arguments_unpacked}'
        return run(cmd)

    def set_(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Set parameters or attributes."""
        return self._run('set', *args, **kwargs)

    def set_parameter(self, parameter: str, value: str) -> CommandResult:
        """Set a specific parameter."""
        return self.set_('parameter', **{parameter: value})

    def set_attribute(self, attribute: str, value: str) -> CommandResult:
        """Set a specific attribute."""
        return self.set_('attribute', **{attribute: value})

    def set_attributes(self, **kwargs: str | None) -> CommandResult:
        """Set multiple attributes at once."""
        return self.set_('attribute', **kwargs)

    def get(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Get parameters or attributes."""
        return self._run('get', *args, **kwargs)

    def get_parameter(self, parameter: str) -> CommandResult:
        """Get a specific parameter."""
        return self.get('parameter', parameter)

    def get_attribute(self, parameter: str) -> CommandResult:
        """Get a specific attribute."""
        return self.get('attribute', parameter)

    def get_attributes(self) -> dict[str, str]:
        """Get all attributes as a dictionary."""
        output = self.get('attribute').stdout.removeprefix('ATTRIBUTE CONFIG GROUP\n======================\n')
        return dict(_.split('=', 1) for _ in output.splitlines() if '=' in _)

    def create(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Create an object."""
        return self._run('create', *args, **kwargs)

    def delete(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Delete an object."""
        return self._run('delete', *args, **kwargs)

    def ls(self) -> CommandResult:
        """List contents."""
        return self._run('ls')

    def get_path(self) -> str:
        """Get the current path."""
        return self.path

    def clearconfig(self) -> CommandResult:
        """Clear the target configuration."""
        return self._run('clearconfig confirm=True')

    @contextmanager
    def temporary_path(self, temp_path: str) -> Generator[None, None, None]:
        """Temporarily change the path for command execution.

        Args:
            temp_path: The temporary path to use
        """
        pathstring = 'path'
        old_value = getattr(self, pathstring)
        setattr(self, pathstring, temp_path)
        yield
        setattr(self, pathstring, old_value)


class Backstore(Targetcli):
    """Base class for backstore operations.

    Args:
        backstore_type: Type of backstore (block, fileio, pscsi, ramdisk)
    """

    def __init__(self, backstore_type: Literal['block', 'fileio', 'pscsi', 'ramdisk']) -> None:
        """Initialize the Backstore instance.

        Args:
            backstore_type: Type of backstore (block, fileio, pscsi, ramdisk)
        """
        self.backstore_type = backstore_type
        super().__init__(path=f'/backstores/{backstore_type}/')


class BackstoreFileio(Backstore):
    """Fileio backstore operations.

    Args:
        name: Name of the backstore
    """

    def __init__(self, name: str) -> None:
        """Initialize the BackstoreFileio instance.

        Args:
            name: Name of the backstore
        """
        self.name = name
        super().__init__(backstore_type='fileio')
        self.backstores_path = self.path
        self.path = f'{self.path}{self.name}'

    def create_backstore(self, size: str, file_or_dev: str) -> CommandResult:
        """Create a fileio backstore.

        Args:
            size: Size of the backstore
            file_or_dev: Path to file or device to use

        Returns:
            CommandResult from creating the backstore
        """
        arguments = {
            'name': self.name,
            'size': size,
            'file_or_dev': file_or_dev,
        }
        with self.temporary_path(self.backstores_path):
            return self.create(**arguments)

    def delete_backstore(self) -> CommandResult:
        """Delete the fileio backstore."""
        with self.temporary_path(self.backstores_path):
            return self.delete(self.name)


class BackstoreBlock(Backstore):
    """Block backstore operations.

    Args:
        name: Name of the backstore
    """

    def __init__(self, name: str) -> None:
        """Initialize the BackstoreBlock instance.

        Args:
            name: Name of the backstore
        """
        self.name = name
        super().__init__(backstore_type='block')
        self.backstores_path = self.path
        self.path = f'{self.path}{self.name}'

    def create_backstore(self, dev: str) -> CommandResult:
        """Create a block backstore.

        Args:
            dev: Path to block device

        Returns:
            CommandResult from creating the backstore
        """
        arguments = {
            'name': self.name,
            'dev': dev,
        }
        with self.temporary_path(self.backstores_path):
            return self.create(**arguments)

    def delete_backstore(self) -> CommandResult:
        """Delete the block backstore."""
        with self.temporary_path(self.backstores_path):
            return self.delete(self.name)


class BackstoreRamdisk(Backstore):
    """Ramdisk backstore operations.

    Args:
        name: Name of the backstore
    """

    def __init__(self, name: str) -> None:
        """Initialize the BackstoreRamdisk instance.

        Args:
            name: Name of the backstore
        """
        self.name = name
        super().__init__(backstore_type='ramdisk')
        self.backstores_path = self.path
        self.path = f'{self.path}{self.name}'

    def create_backstore(self, size: str) -> CommandResult:
        """Create a ramdisk backstore.

        Args:
            size: Size of the ramdisk

        Returns:
            CommandResult from creating the backstore
        """
        arguments = {
            'name': self.name,
            'size': size,
        }
        with self.temporary_path(self.backstores_path):
            return self.create(**arguments)

    def delete_backstore(self) -> CommandResult:
        """Delete the ramdisk backstore."""
        with self.temporary_path(self.backstores_path):
            return self.delete(self.name)


class Iscsi(Targetcli):
    """iSCSI target operations.

    Args:
        target_wwn: Target WWN (World Wide Name)
        tpg: Target Portal Group number (default: 1)
    """

    def __init__(self, target_wwn: str, tpg: int = 1) -> None:
        """Initialize the Iscsi instance.

        Args:
            target_wwn: Target WWN (World Wide Name)
            tpg: Target Portal Group number (default: 1)
        """
        self.target_wwn = target_wwn
        self.tpg = tpg
        self.iscsi_path = '/iscsi/'
        self.target_path = f'{self.iscsi_path}{target_wwn}/tpg{tpg}/'
        super().__init__(path=self.target_path)

    def create_target(self) -> CommandResult:
        """Create an iSCSI target."""
        with self.temporary_path(self.iscsi_path):
            return self.create(wwn=self.target_wwn)

    def delete_target(self) -> CommandResult:
        """Delete the iSCSI target."""
        with self.temporary_path(self.iscsi_path):
            return self.delete(wwn=self.target_wwn)

    def set_discovery_auth(
        self,
        userid: str | None = None,
        password: str | None = None,
        mutual_userid: str | None = None,
        mutual_password: str | None = None,
    ) -> CommandResult:
        """Set discovery authentication.

        Args:
            userid: User ID for authentication (None becomes empty string)
            password: Password for authentication (None becomes empty string)
            mutual_userid: Mutual User ID for authentication (None becomes empty string)
            mutual_password: Mutual Password for authentication (None becomes empty string)

        Returns:
            CommandResult from setting discovery auth
        """
        with self.temporary_path(self.iscsi_path):
            # Passing empty strings in one command does not work
            self.set_('discovery_auth', userid='' if userid is None else userid)
            self.set_('discovery_auth', password='' if password is None else password)
            self.set_('discovery_auth', mutual_userid='' if mutual_userid is None else mutual_userid)
            self.set_('discovery_auth', mutual_password='' if mutual_password is None else mutual_password)
            return self.set_('discovery_auth', enable='1')

    def disable_discovery_auth(self) -> CommandResult:
        """Disable discovery authentication."""
        with self.temporary_path(self.iscsi_path):
            return self.set_('discovery_auth', enable='0')


class TPG(Targetcli):
    """Target Portal Group operations.

    Args:
        target_wwn: Target WWN (World Wide Name)
        tpg: Target Portal Group number (default: 1)
    """

    def __init__(self, target_wwn: str, tpg: int = 1) -> None:
        """Initialize the TPG instance.

        Args:
            target_wwn: Target WWN (World Wide Name)
            tpg: Target Portal Group number (default: 1)
        """
        self.target_wwn = target_wwn
        self.tpg = tpg
        self.target_path = f'/iscsi/{target_wwn}/'
        self.tpg_path = f'{self.target_path}tpg{tpg}/'
        super().__init__(path=self.tpg_path)

    def create_tpg(self) -> CommandResult:
        """Create a Target Portal Group."""
        with self.temporary_path(self.target_path):
            return self.create(tag=str(self.tpg))

    def delete_tpg(self) -> CommandResult:
        """Delete the Target Portal Group."""
        with self.temporary_path(self.target_path):
            return self.delete(tag=str(self.tpg))

    def enable_tpg(self) -> CommandResult:
        """Enable the Target Portal Group."""
        return self._run('enable')

    def disable_tpg(self) -> CommandResult:
        """Disable the Target Portal Group."""
        return self._run('disable')

    def set_auth(
        self,
        userid: str | None = None,
        password: str | None = None,
        mutual_userid: str | None = None,
        mutual_password: str | None = None,
    ) -> CommandResult:
        """Set authentication for the Target Portal Group.

        Args:
            userid: User ID for authentication (None becomes empty string)
            password: Password for authentication (None becomes empty string)
            mutual_userid: Mutual User ID for authentication (None becomes empty string)
            mutual_password: Mutual Password for authentication (None becomes empty string)

        Returns:
            CommandResult from setting auth
        """
        self.set_('auth', userid='' if userid is None else userid)
        self.set_('auth', password='' if password is None else password)
        self.set_('auth', mutual_userid='' if mutual_userid is None else mutual_userid)
        self.set_('auth', mutual_password='' if mutual_password is None else mutual_password)
        return self.set_('attribute', authentication='1', generate_node_acls='1')

    def disable_auth_per_tpg(self) -> CommandResult:
        """Disable authentication for the Target Portal Group."""
        return self.set_('attribute', authentication='0')

    def disable_generate_node_acls(self) -> CommandResult:
        """Disable generate_node_acls for the Target Portal Group."""
        return self.set_('attribute', generate_node_acls='0')


class LUN(Targetcli):
    """LUN operations."""

    def create_lun(self, storage_object: str) -> CommandResult:
        """Create a LUN.

        Args:
            storage_object: Path to storage object

        Returns:
            CommandResult from creating the LUN
        """
        return self.create(storage_object)

    def delete_lun(self, lun_number: int) -> CommandResult:
        """Delete a LUN.

        Args:
            lun_number: LUN number to delete

        Returns:
            CommandResult from deleting the LUN
        """
        return self.delete(str(lun_number))


class IscsiLUN(LUN):
    """LUN operations.

    Args:
        target_wwn: Target WWN (World Wide Name)
        tpg: Target Portal Group number (default: 1)
    """

    def __init__(self, target_wwn: str, tpg: int = 1) -> None:
        """Initialize the iSCSI LUN instance.

        Args:
            target_wwn: Target WWN (World Wide Name)
            tpg: Target Portal Group number (default: 1)
        """
        super().__init__(path=f'/iscsi/{target_wwn}/tpg{tpg}/luns/')


class Loopback(Targetcli):
    """Manages loopback target devices in targetcli.

    This class handles the creation and deletion of loopback targets using targetcli,
    with optional WWN (World Wide Name) specification. It extends the Targetcli base class
    to provide loopback-specific functionality.

    Attributes:
        target_wwn: The World Wide Name of the target device.
                    If None, a WWN will be automatically generated during target creation.
        loopback_path: The base path for loopback devices in targetcli.
        target_path: The full path to this specific target in targetcli.

    Example:
        Create a loopback target with a custom WWN:

        >>> loopback = Loopback(target_wwn='naa.5001234567890')
        >>> result = loopback.create_target()
        >>> if result.succeeded:
        ...     print(f'Created loopback target: {loopback.target_wwn}')
    """

    def __init__(self, target_wwn: str | None = None) -> None:
        """Initialize a new Loopback target instance.

        Args:
            target_wwn: Optional WWN for the target. If not provided, a WWN will be
                generated automatically when creating the target.
        """
        self.target_wwn = target_wwn
        self.loopback_path = '/loopback/'
        self.target_path = f'{self.loopback_path}{target_wwn}/' if target_wwn else self.loopback_path
        super().__init__(path=self.target_path)

    def create_target(self) -> CommandResult:
        """Create a new loopback target.

        If target_wwn was not provided during initialization, this method will create
        a target with an automatically generated WWN and update the target_wwn attribute
        with the generated value.

        Returns:
            CommandResult: Result of the target creation command, containing success status
                and command output.

        Note:
            When creating a target without a specified WWN, the method extracts the
            generated WWN from the command output using a regular expression matching
            'naa.' followed by alphanumeric characters.
        """
        with self.temporary_path(self.loopback_path):
            if not self.target_wwn:
                ret = self.create()
                if ret.succeeded:
                    match = re.search(r'naa\.\w+', ret.stdout)
                    if match:
                        self.target_wwn = match.group(0)
                        self.target_path = f'{self.loopback_path}{self.target_wwn}/'
                return ret
            return self.create(wwn=self.target_wwn)

    def delete_target(self) -> CommandResult:
        """Delete the loopback target.

        Returns:
            CommandResult: Result of the target deletion command, containing success status
                and command output.

        Raises:
            ValueError: If target_wwn is None when attempting to delete the target.
        """
        if not self.target_wwn:
            raise ValueError('Cannot delete target: target_wwn is not set')

        with self.temporary_path(self.loopback_path):
            return self.delete(wwn=self.target_wwn)


class LoopbackLUN(LUN):
    """Manages LUNs (Logical Unit Numbers) for a loopback target.

    This class provides functionality for managing LUN associated with a specific
    loopback target identified by its WWN.

    Attributes:
        Inherits all attributes from the LUN base class.

    Example:
        ```python
        >>> luns = LoopbackLUN(target_wwn='naa.5001234567890')
        >>> # Use LUN class methods to manage logical units
        ```
    """

    def __init__(self, target_wwn: str) -> None:
        """Initialize LoopbackLUN for a specific target.

        Args:
            target_wwn: The World Wide Name of the target device for which to manage LUN.

        Raises:
            ValueError: If target_wwn is empty or invalid.
        """
        if not target_wwn:
            raise ValueError('target_wwn cannot be empty')

        super().__init__(path=f'/loopback/{target_wwn}/luns/')


class ACL(Targetcli):
    """ACL operations.

    Args:
        target_wwn: Target WWN (World Wide Name)
        initiator_wwn: Initiator WWN
        tpg: Target Portal Group number (default: 1)
    """

    def __init__(self, target_wwn: str, initiator_wwn: str, tpg: int = 1) -> None:
        """Initialize the ACL instance.

        Args:
            target_wwn: Target WWN (World Wide Name)
            initiator_wwn: Initiator WWN
            tpg: Target Portal Group number (default: 1)
        """
        self.target_wwn = target_wwn
        self.initiator_wwn = initiator_wwn
        self.acls_path = f'/iscsi/{target_wwn}/tpg{tpg}/acls/'
        super().__init__(path=f'{self.acls_path}{initiator_wwn}')

    def create_acl(self) -> CommandResult:
        """Create an ACL."""
        with self.temporary_path(self.acls_path):
            return self.create(wwn=self.initiator_wwn)

    def delete_acl(self) -> CommandResult:
        """Delete the ACL."""
        with self.temporary_path(self.acls_path):
            return self.delete(wwn=self.initiator_wwn)

    def set_auth(
        self,
        userid: str | None = None,
        password: str | None = None,
        mutual_userid: str | None = None,
        mutual_password: str | None = None,
    ) -> CommandResult:
        """Set authentication for the ACL.

        Args:
            userid: User ID for authentication (None becomes empty string)
            password: Password for authentication (None becomes empty string)
            mutual_userid: Mutual User ID for authentication (None becomes empty string)
            mutual_password: Mutual Password for authentication (None becomes empty string)

        Returns:
            CommandResult from setting auth
        """
        self.set_('auth', userid='' if userid is None else userid)
        self.set_('auth', password='' if password is None else password)
        self.set_('auth', mutual_userid='' if mutual_userid is None else mutual_userid)
        self.set_('auth', mutual_password='' if mutual_password is None else mutual_password)
        return self.set_('attribute', authentication='1')

    def disable_auth(self) -> CommandResult:
        """Disable authentication for the ACL."""
        return self.set_('attribute', authentication='0')

    def map_lun(
        self,
        mapped_lun: int,
        tpg_lun_or_backstore: str,
        *,
        write_protect: bool = False,
    ) -> CommandResult:
        """Map a LUN to the ACL.

        Args:
            mapped_lun: LUN number to map
            tpg_lun_or_backstore: Path to TPG LUN or backstore
            write_protect: Whether to write protect the LUN

        Returns:
            CommandResult from mapping the LUN
        """
        return self.create(
            mapped_lun=str(mapped_lun),
            tpg_lun_or_backstore=tpg_lun_or_backstore,
            write_protect=str(write_protect),
        )


class Portal(Targetcli):
    """Portal operations.

    Args:
        target_wwn: Target WWN (World Wide Name)
        portal: Portal address
        tpg: Target Portal Group number (default: 1)
        ip_port: Portal IP port (default: 3260)
    """

    def __init__(self, target_wwn: str, portal: str, tpg: int = 1, ip_port: int = 3260) -> None:
        """Initialize the Portal instance.

        Args:
            target_wwn: Target WWN (World Wide Name)
            portal: Portal address
            tpg: Target Portal Group number (default: 1)
            ip_port: Portal IP port (default: 3260)
        """
        self.portal = portal
        self.ip_port = str(ip_port)
        self.portals_path = f'/iscsi/{target_wwn}/tpg{tpg}/portals/'
        self.portal_path = f'{self.portals_path}{self.portal}:{self.ip_port}'
        super().__init__(path=self.portal_path)

    def create_portal(self) -> CommandResult:
        """Create a portal."""
        with self.temporary_path(self.portals_path):
            return self.create(ip_address=self.portal, ip_port=self.ip_port)

    def delete_portal(self) -> CommandResult:
        """Delete the portal."""
        with self.temporary_path(self.portals_path):
            return self.delete(ip_address=self.portal, ip_port=self.ip_port)

    def enable_offload(self) -> CommandResult:
        """Enable offload for the portal."""
        return self._run('enable_offload=True')

    def disable_offload(self) -> CommandResult:
        """Disable offload for the portal."""
        return self._run('enable_offload=False')


def create_basic_iscsi_target(
    target_wwn: str = '',
    initiator_wwn: str = '',
    size: str = '1G',
    userid: str | None = None,
    password: str | None = None,
    mutual_userid: str | None = None,
    mutual_password: str | None = None,
) -> bool:
    """Create simple iSCSI target using fileio backstore.

    Args:
        target_wwn: Target WWN (World Wide Name)
        initiator_wwn: Initiator WWN
        size: Size of the fileio backstore
        userid: User ID for authentication (None becomes empty string)
        password: Password for authentication (None becomes empty string)
        mutual_userid: Mutual User ID for authentication (None becomes empty string)
        mutual_password: Mutual Password for authentication (None becomes empty string)

    Returns:
        bool: True if target creation was successful
    """
    if not target_wwn:
        target_wwn = f'iqn.2023-01.com.sts:target:{uuid4().hex[-9:]}'
    if not initiator_wwn:
        try:
            # Try to set localhost initiatorname
            initiator_wwn = Path('/etc/iscsi/initiatorname.iscsi').read_text().split('=')[1]
        except FileNotFoundError:
            initiator_wwn = f'iqn.1994-05.com.redhat:{uuid4().hex[-9:]}'
        logging.info(f'Initiator iqn: "{initiator_wwn}"')
    backstore_name = initiator_wwn.split(':')[1]

    backstore = BackstoreFileio(name=backstore_name)
    backstore.create_backstore(size=size, file_or_dev=f'{backstore_name}_backstore_file')
    Iscsi(target_wwn=target_wwn).create_target()
    IscsiLUN(target_wwn=target_wwn).create_lun(storage_object=backstore.path)
    acl = ACL(target_wwn=target_wwn, initiator_wwn=initiator_wwn)
    acl.create_acl()
    if userid and password:
        acl.set_auth(
            userid=userid,
            password=password,
            mutual_userid=mutual_userid,
            mutual_password=mutual_password,
        )
    else:
        acl.disable_auth()
    return True


def create_loopback_devices(count: int, block_size: int = 4096) -> list[BlockDevice]:
    """Create a specified number of loopback devices with given block size.

    Creates loopback devices by setting up a target with LUNs (Logical Unit Numbers),
    each backed by a file. The devices are created with specified parameters or
    environment variable defaults.

    Args:
        count: Number of loopback devices to create
        block_size: Block size in bytes for the devices (default: 4096)

    Returns:
        list[BlockDevice]: List of created block devices that match the LUN prefix

    Raises:
        AssertionError: If any step of device creation fails (target creation,
            backstore creation, attribute setting, or LUN creation)
        ValueError: If count is less than 1

    Environment Variables:
        TARGET_WWN: World Wide Name for the target (default: 'naa.50014054c1441891')
        LOOPBACK_DEVICE_SIZE: Size of each device (default: '2G')
        LUN_PREFIX: Prefix for LUN names (default: 'common-lun-')
        IMAGE_PATH: Path where backing files are created (default: '/var/tmp/')

    Example:
        ```python
        >>> devices = create_loopback_devices(2, block_size=512)
        >>> print(f'Created {len(devices)} devices')
        ```
    """
    if count < 1:
        raise ValueError('Device count must be at least 1')

    # Get configuration from environment variables
    wwn = getenv('TARGET_WWN', 'naa.50014054c1441891')
    device_size = getenv('LOOPBACK_DEVICE_SIZE', '2G')
    lun_prefix = getenv('LUN_PREFIX', 'common-lun-')
    image_path = getenv('IMAGE_PATH', '/var/tmp/')
    suffix = '.image'

    # Initialize loopback target and LUN
    loopback = Loopback(target_wwn=wwn)
    lun = LoopbackLUN(target_wwn=wwn)

    # Create target
    result = loopback.create_target()
    assert result.succeeded, f'Failed to create target: {result.stderr}'

    # Create each device
    for n in range(count):
        backstore = BackstoreFileio(name=f'{lun_prefix}{n}')

        # Create backstore
        result = backstore.create_backstore(size=device_size, file_or_dev=f'{image_path}{lun_prefix}{n}{suffix}')
        assert result.succeeded, f'Failed to create backstore {n}: {result.stderr}'

        # Set block size
        result = backstore.set_attribute(attribute='block_size', value=str(block_size))
        assert result.succeeded, f'Failed to set block size for device {n}: {result.stderr}'

        # Create LUN
        result = lun.create(storage_object=backstore.path)
        assert result.succeeded, f'Failed to create LUN {n}: {result.stderr}'

    return [device for device in get_free_disks() if device.model and lun_prefix in device.model]


def cleanup_loopback_devices(devices: list[BlockDevice]) -> None:
    """Clean up loopback devices and associated resources.

    Removes the LUNs, backstores, and target associated with the provided devices.
    The cleanup is performed in reverse order of creation to ensure proper resource
    cleanup.

    Args:
        devices: List of BlockDevice objects to clean up

    Raises:
        AssertionError: If any step of the cleanup process fails (LUN deletion,
            backstore deletion, or target deletion)
        ValueError: If devices list is empty

    Environment Variables:
        TARGET_WWN: World Wide Name for the target (default: 'naa.50014054c1441891')
        LUN_PREFIX: Prefix for LUN names (default: 'common-lun-')

    Example:
        ```python
        >>> devices = create_loopback_devices(2)
        >>> cleanup_loopback_devices(devices)
        ```
    """
    if not devices:
        raise ValueError('No devices provided for cleanup')

    # Get configuration from environment variables
    wwn = getenv('TARGET_WWN', 'naa.50014054c1441891')
    lun_prefix = getenv('LUN_PREFIX', 'common-lun-')

    # Initialize loopback target and LUN
    loopback = Loopback(target_wwn=wwn)
    lun = LoopbackLUN(target_wwn=wwn)

    # Clean up each device
    for n in range(len(devices)):
        backstore = BackstoreFileio(name=f'{lun_prefix}{n}')

        # Delete LUN
        result = lun.delete_lun(n)
        assert result.succeeded, f'Failed to delete LUN {n}: {result.stderr}'

        # Delete backstore
        result = backstore.delete_backstore()
        assert result.succeeded, f'Failed to delete backstore {n}: {result.stderr}'

    # Delete target
    result = loopback.delete_target()
    assert result.succeeded, f'Failed to delete target: {result.stderr}'
