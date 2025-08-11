# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Stratis pool management.

This module provides functionality for managing Stratis pools:
- Pool creation
- Pool operations
- Pool encryption
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal

import pytest

from sts.blockdevice import get_free_disks
from sts.stratis.base import StratisBase, StratisConfig, StratisOptions
from sts.stratis.errors import StratisPoolError
from sts.utils.cmdline import run

# Type aliases
UnlockMethod = Literal['keyring', 'clevis', 'any']

PoolData = dict[str, Any]
PoolsData = list[PoolData]
ReportData = dict[str, Any]


@dataclass
class BlockDevInfo:
    """Block device information from stratis report.

    Args:
        path: Device path
        size: Device size in sectors
        uuid: Device UUID
        in_use: Whether device is in use
        blksizes: Block size information
    """

    path: str | None = None
    size: str | None = None
    uuid: str | None = None
    in_use: bool = False
    blksizes: str | None = None
    clevis_config: dict[str, Any] | None = None
    clevis_pin: str | None = None
    key_description: str | None = None

    @staticmethod
    def parse_bool(value: bool | int | str | None) -> bool:  # noqa: FBT001
        """Parse boolean value from stratis output.

        Args:
            value: Value to parse (can be bool, int, str, or None)

        Returns:
            Parsed boolean value
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlockDevInfo:
        """Create device info from dictionary.

        Args:
            data: Dictionary data

        Returns:
            BlockDevInfo instance
        """
        return cls(
            path=data.get('path'),
            size=data.get('size'),
            uuid=data.get('uuid'),
            in_use=cls.parse_bool(data.get('in_use')),
            blksizes=data.get('blksizes'),
            key_description=data.get('key_description'),
            clevis_pin=data.get('clevis_pin'),
            clevis_config=data.get('clevis_config'),
        )


@dataclass
class BlockDevs:
    """Block devices from stratis report.

    Args:
        datadevs: List of data devices
        cachedevs: List of cache devices
    """

    datadevs: list[BlockDevInfo] = field(default_factory=list)
    cachedevs: list[BlockDevInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlockDevs:
        """Create block devices from dictionary.

        Args:
            data: Dictionary data

        Returns:
            BlockDevs instance
        """
        return cls(
            datadevs=[BlockDevInfo.from_dict(dev) for dev in data.get('datadevs', [])],
            cachedevs=[BlockDevInfo.from_dict(dev) for dev in data.get('cachedevs', [])],
        )


@dataclass
class PoolReport(StratisBase):
    """Pool report data.

    This class provides detailed information about a Stratis pool:
    - Direct report fetching
    - Refreshable data
    - Complete pool information

    Args:
        name: Pool name (optional)
        uuid: Pool UUID (optional)
        blockdevs: Block devices (optional)
        encryption: Encryption type (optional)
        fs_limit: Filesystem limit (optional)
        available_actions: Available actions (optional)
        filesystems: List of filesystems (optional)
        raw_data: Raw pool data from report
        total_size: Total pool size in sectors (optional)
        used_size: Used size of pool in sectors (optional)
        object_path: Pool Dbus object path
        prevent_update: Flag to prevent updates from report (defaults to False)
    """

    name: str | None = None
    blockdevs: BlockDevs = field(default_factory=BlockDevs)
    uuid: str | None = None
    encryption: dict[str, Any] = field(default_factory=dict)
    fs_limit: int | None = None
    available_actions: str | None = None
    filesystems: list[Any] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict, repr=False)
    total_size: int | None = field(default=None)
    used_size: int | None = field(default=None)
    object_path: str | None = field(default=None)
    prevent_update: bool = field(default=False)

    def __post_init__(self) -> None:
        """Initialize the report with default config."""
        super().__init__(config=StratisConfig())

        # If name is provided, fetch the report data
        if self.name:
            self.refresh()

    def refresh(self) -> bool:
        """Refresh pool report data from system.

        Updates all fields with the latest information from stratisd.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        # If prevent_update is True, skip refresh
        if self.prevent_update:
            logging.debug('Refresh skipped due to prevent_update flag')
            return True

        # First get standard report data
        result = self.run_command('report')
        if result.failed or not result.stdout:
            logging.error('Failed to get report data')
            return False

        try:
            report_data = json.loads(result.stdout)
            if not self._update_from_report(report_data):
                return False

            # If we have a name, also fetch size information from managed objects
            if self.name:
                self.update_from_managed_objects()

        except json.JSONDecodeError:
            logging.exception('Failed to parse report JSON')
            return False
        else:
            return True

    def update_from_managed_objects(self) -> bool:
        """Update size information from managed objects.

        Fetches encryption information, total and used size from the managed objects interface.

        Returns:
            bool: True if successful, False otherwise
        """
        if self.prevent_update:
            logging.debug('Size info update skipped due to prevent_update flag')
            return True

        if not self.name:
            return False

        # Get object path
        result = self.run_command(
            subcommand='pool', action='debug get-object-path', positional_args=['--name', self.name]
        )

        if result.failed or not result.stdout:
            logging.debug(f'Failed to get object path for pool {self.name}')
            return False

        self.object_path = result.stdout.strip()

        # Get managed objects report
        result = self.run_command(subcommand='report', action='managed_objects_report')

        if result.failed or not result.stdout:
            logging.error('Failed to get managed objects report')
            return False

        try:
            report_data = json.loads(result.stdout)

            # Get pool data (if object_path exists in report)
            if self.object_path not in report_data:
                logging.error(f'Object path {self.object_path} not found in managed objects report')
                return False

            # Get the pool interfaces
            pool_interfaces = report_data[self.object_path]

            # Get the last revision
            last_revision = list(pool_interfaces.keys())[-1]
            pool_interface = pool_interfaces[last_revision]

            # metadata version 2 uses different keys for the encryption info
            if (
                pool_interface['Encrypted'] == 1
                and 'MetadataVersion' in pool_interface
                and pool_interface['MetadataVersion'] == 2
            ):
                if 'KeyDescriptions' in pool_interface and pool_interface['KeyDescriptions'] != []:
                    self.encryption['KeyDescriptions'] = pool_interface['KeyDescriptions']
                if 'ClevisInfos' in pool_interface and pool_interface['ClevisInfos'] != []:
                    self.encryption['ClevisInfos'] = pool_interface['ClevisInfos']
            elif pool_interface['Encrypted'] == 1:
                if 'KeyDescription' in pool_interface and pool_interface['KeyDescription'] != []:
                    self.encryption['KeyDescriptions'] = pool_interface['KeyDescription']
                if 'ClevisInfo' in pool_interface and pool_interface['ClevisInfo'] != []:
                    self.encryption['ClevisInfos'] = pool_interface['ClevisInfo']

            # Get size information
            if 'TotalPhysicalSize' in pool_interface:
                self.total_size = int(pool_interface['TotalPhysicalSize'])

            # TotalPhysicalUsed is a tuple with format [1, "value"]
            if 'TotalPhysicalUsed' in pool_interface and (
                isinstance(pool_interface['TotalPhysicalUsed'], list) and len(pool_interface['TotalPhysicalUsed']) > 1
            ):
                self.used_size = int(pool_interface['TotalPhysicalUsed'][1])

        except (json.JSONDecodeError, KeyError, ValueError):
            logging.exception('Error parsing managed objects data')
            return False
        else:
            return True

    def _update_from_report(self, report_data: ReportData) -> bool:
        """Update pool information from report data.

        Args:
            report_data: Complete report data

        Returns:
            bool: True if update was successful, False otherwise
        """
        if self.prevent_update:
            logging.debug('Update from report skipped due to prevent_update flag')
            return True

        if not isinstance(report_data, dict) or 'pools' not in report_data:
            logging.error('Invalid report format')
            return False

        pools = report_data.get('pools', [])
        if not isinstance(pools, list):
            logging.error('Invalid pools format')
            return False

        # Find the pool with matching name
        for pool in pools:
            if not isinstance(pool, dict):
                continue

            if not self.name or self.name == pool.get('name'):
                # Store raw data for access to fields not explicitly mapped
                self.raw_data = pool.copy()

                # Update explicit fields
                self.name = pool.get('name')
                self.uuid = pool.get('uuid')
                self.fs_limit = pool.get('fs_limit')
                self.available_actions = pool.get('available_actions')
                self.filesystems = pool.get('filesystems', [])

                # Update blockdevs if present
                if 'blockdevs' in pool:
                    self.blockdevs = BlockDevs.from_dict(pool.get('blockdevs', {}))

                return True

        # If we get here and name was specified, pool wasn't found
        if self.name:
            logging.warning(f"Pool '{self.name}' not found in report")
            return False

        # If no name was specified and no pools exist
        if not pools:
            logging.warning('No pools found in report')
            return False

        return False

    def get_device_paths(self) -> list[str]:
        """Get all device paths from the pool.

        Returns:
            List of device paths for both data and cache devices
        """
        return [dev.path for dev in self.blockdevs.datadevs if dev.path] + [
            dev.path for dev in self.blockdevs.cachedevs if dev.path
        ]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoolReport | None:
        """Create report from dictionary.

        Args:
            data: Dictionary data

        Returns:
            PoolReport instance or None if invalid
        """
        try:
            report = cls()
            report.raw_data = data.copy()

            report.name = data.get('name')
            report.blockdevs = BlockDevs.from_dict(data.get('blockdevs', {}))
            report.uuid = data.get('uuid')
            report.fs_limit = data.get('fs_limit')
            report.available_actions = data.get('available_actions')
            report.filesystems = data.get('filesystems', [])
            report.encryption = data.get('encryption', {})

            # Fetch size info if name is provided
            if report.name:
                report.update_from_managed_objects()

        except (KeyError, TypeError) as e:
            logging.warning(f'Invalid pool report data: {e}')
            return None
        else:
            return report

    @classmethod
    def get_all(cls) -> list[PoolReport]:
        """Get reports for all pools.

        Returns:
            List of PoolReport instances
        """
        reports: list[PoolReport] = []

        # Create base instance
        base = cls()

        result = base.run_command('report')
        if result.failed or not result.stdout:
            return reports

        try:
            report_data = json.loads(result.stdout)

            if 'pools' in report_data and isinstance(report_data['pools'], list):
                for pool_data in report_data['pools']:
                    if not isinstance(pool_data, dict):
                        continue

                    if report := cls.from_dict(pool_data):
                        reports.append(report)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.warning(f'Failed to parse pools: {e}')

        return reports


@dataclass
class PoolCreateConfig:
    """Pool creation configuration.

    Args:
        key_desc: Key description for keyring encryption (optional)
        tang_url: Tang server URL for tang encryption (optional)
        thumbprint: Tang server thumbprint (optional)
        clevis: Clevis encryption configuration (optional)
        trust_url: Trust Tang server URL (optional)
        no_overprovision: Disable overprovisioning (optional)
        integrity: Integrity options (pre-allocate | no) (optional)
        journal_size: Size of integrity device's journal (optional)
        tag_spec: Tag specification for integrity (optional)

    Example:
        ```python
        config = PoolCreateConfig()  # Uses defaults
        config = PoolCreateConfig(key_desc='mykey')  # Custom settings
        config = PoolCreateConfig(integrity='pre-allocate', journal_size='64KiB', tag_spec='32b')  # With integrity
        ```
    """

    # Optional parameters
    key_desc: str | None = None
    tang_url: str | None = None
    thumbprint: str | None = None
    clevis: str | None = None
    trust_url: bool = False
    no_overprovision: bool = False

    # Integrity options
    integrity: str | None = None
    journal_size: int | None = None
    tag_spec: str | None = None


@dataclass
class TangConfig:
    """Tang server configuration.

    Args:
        url: Tang server URL (optional, discovered from system)
        trust_url: Trust server URL (optional)
        thumbprint: Server thumbprint (optional)

    Example:
        ```python
        config = TangConfig()  # Uses defaults
        config = TangConfig(url='http://tang.example.com')  # Custom settings
        ```
    """

    # Optional parameters
    url: str | None = None
    trust_url: bool = False
    thumbprint: str | None = None


@dataclass
class StratisPool(StratisBase):
    """Stratis pool representation.

    This class provides functionality for managing Stratis pools:
    - Pool creation
    - Pool operations
    - Pool encryption

    Args:
        name: Pool name (optional, discovered from system)
        uuid: Pool UUID (optional, discovered from system)
        encryption: Encryption type (optional, discovered from system)
        blockdevs: List of block devices (optional, discovered from system)
        report: Pool report (optional, discovered from system)

    Example:
        ```python
        pool = StratisPool()  # Discovers first available pool
        pool = StratisPool(name='pool1')  # Discovers other values
        ```
    """

    name: str | None = None
    uuid: str | None = None
    encryption: dict[str, Any] = field(default_factory=dict)
    blockdevs: list[str] = field(default_factory=list)
    report: PoolReport | None = field(default=None, repr=False)
    prevent_report_updates: bool = False

    # Class-level paths
    POOL_PATH: ClassVar[str] = '/stratis/pool'

    def __post_init__(self) -> None:
        """Initialize pool."""
        # Initialize base class with default config
        super().__init__(config=StratisConfig())

        if self.name and not self.report:
            self.report = PoolReport(name=self.name, prevent_update=self.prevent_report_updates)
            if not self.prevent_report_updates:
                self._update_from_report()

    def _update_from_report(self) -> None:
        """Update pool attributes from report data.

        This centralizes all attribute updates from the report to avoid inconsistencies.
        """
        if self.prevent_report_updates:
            logging.debug('Update from report skipped due to prevent_report_updates flag')
            return

        if not self.report:
            return

        if not self.name and self.report.name:
            self.name = self.report.name

        if not self.uuid and self.report.uuid:
            self.uuid = self.report.uuid

        if self.report.encryption:
            self.encryption = self.report.encryption

        if not self.blockdevs:
            self.blockdevs = self.report.get_device_paths()

    def refresh_report(self) -> bool:
        """Refresh pool report data.

        Creates or updates the pool report with the latest information.

        Returns:
            bool: True if refresh was successful
        """
        # Create new report if needed
        if not self.report:
            # Set name after init because we are explicitly calling refresh below
            # Setting name at init would result in calling .refresh() twice
            self.report = PoolReport(prevent_update=self.prevent_report_updates)
            self.report.name = self.name

        # Refresh the report data
        success = self.report.refresh()

        # Update pool fields from report if successful
        if success and not self.prevent_report_updates:
            self._update_from_report()

        return success

    def create(self, config: PoolCreateConfig | None = None) -> bool:
        """Create pool.

        Args:
            config: Pool creation configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.create(PoolCreateConfig(key_desc='mykey'))
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        if not self.blockdevs:
            raise StratisPoolError('No block devices specified')

        options: StratisOptions = {}
        if config:
            if config.key_desc:
                options['--key-desc'] = config.key_desc
            if config.clevis:
                options['--clevis'] = config.clevis
            if config.tang_url:
                options['--tang-url'] = config.tang_url
            if config.thumbprint:
                options['--thumbprint'] = config.thumbprint
            if config.trust_url:
                options['--trust-url'] = None
            if config.no_overprovision:
                options['--no-overprovision'] = None

        result = self.run_command(
            subcommand='pool',
            action='create',
            options=options,
            positional_args=[self.name, ' '.join(self.blockdevs)],
        )

        if not result.failed:
            return self.refresh_report()

        return False

    def destroy(self) -> bool:
        """Destroy pool.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.destroy()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='destroy',
            positional_args=[self.name],
        )
        return not result.failed

    def list(self, *, stopped: bool = False, current_pool: bool = True) -> str:
        """List information about pools.

        Args:
            stopped: Display information about stopped pools only
            current_pool: Display information about all pools

        Returns:
            stdout if successful, None otherwise

        Example:
            ```python
            pool.list(stopped=True)
            Name              Total / Used / Free    Properties                                   UUID   Alerts
            p1     7.28 TiB / 4.21 GiB / 7.27 TiB   ~Ca,~Cr, Op   398925ee-6efa-4fe1-bc0f-9cd13e3da8d7
            ```
        """
        options: StratisOptions = {}
        if current_pool:
            if self.uuid:
                options['--uuid'] = self.uuid
            else:
                options['--name'] = self.name
        if stopped:
            options['--stopped'] = ''

        result = self.run_command('pool', action='list', options=options)
        return result.stdout

    def start(self, unlock_method: UnlockMethod | None = None, token_slot: int | None = None) -> bool:
        """Start pool.

        Args:
            unlock_method: Encryption unlock method

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.start(unlock_method='keyring')
            True
            ```
        """
        if not self.name and not self.uuid:
            logging.error('Pool name or UUID required')
            return False

        options: StratisOptions = {}
        if unlock_method:
            options['--unlock-method'] = unlock_method
        if token_slot is not None:
            options['--token-slot'] = str(token_slot)
        if self.uuid:
            options['--uuid'] = self.uuid
        else:
            options['--name'] = self.name
        result = self.run_command('pool', action='start', options=options)

        if not result.failed:
            self.refresh_report()

        return not result.failed

    def stop(self) -> bool:
        """Stop pool.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.stop()
            True
            ```
        """
        if not self.name and not self.uuid:
            logging.error('Pool name or UUID required')
            return False

        options: StratisOptions = {}
        if self.uuid:
            options['--uuid'] = self.uuid
        else:
            options['--name'] = self.name

        result = self.run_command('pool', action='stop', options=options)
        return not result.failed

    def add_data(self, blockdevs: list[str]) -> bool:
        """Add data devices to pool.

        Args:
            blockdevs: List of block devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.add_data(['/dev/sdd', '/dev/sde'])
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='add-data',
            positional_args=[self.name, ' '.join(blockdevs)],
        )

        logging.info(result)

        if not result.failed:
            self.refresh_report()

        return not result.failed

    def extend_data(self) -> bool:
        """Extend data devices in the pool to use the full device size.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.extend_data()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='extend-data',
            positional_args=[self.name],
        )

        if not result.failed:
            self.refresh_report()

        return not result.failed

    def init_cache(self, blockdevs: list[str]) -> bool:
        """Initialize cache devices.

        Args:
            blockdevs: List of block devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.init_cache(['/dev/nvme0n1'])
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        # Pass each device as a separate argument
        result = self.run_command(
            subcommand='pool',
            action='init-cache',
            positional_args=[self.name, *blockdevs],
        )

        if not result.failed:
            self.refresh_report()
        else:
            logging.error(f'Failed to initialize cache: {result.stderr}')

        return not result.failed

    def add_cache(self, blockdevs: list[str]) -> bool:
        """Add cache devices to pool.

        Args:
            blockdevs: List of block devices

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.add_cache(['/dev/nvme0n2'])
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='add-cache',
            positional_args=[self.name, ' '.join(blockdevs)],
        )
        if not result.failed:
            self.refresh_report()

        return not result.failed

    def bind_keyring(self, key_desc: str) -> bool:
        """Bind pool to keyring.

        Args:
            key_desc: Key description

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.bind_keyring('mykey')
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='bind keyring',
            positional_args=[self.name, key_desc],
        )
        if not result.failed:
            self.refresh_report()

        return not result.failed

    def bind_tang(self, config: TangConfig) -> bool:
        """Bind pool to Tang server.

        Args:
            config: Tang server configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.bind_tang(TangConfig('http://tang.example.com'))
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        if not config.url:
            logging.error('Tang server URL required')
            return False

        options: StratisOptions = {}
        if config.trust_url:
            options['--trust-url'] = None
        if config.thumbprint:
            options['--thumbprint'] = config.thumbprint

        result = self.run_command(
            subcommand='pool',
            action='bind tang',
            options=options,
            positional_args=[self.name, config.url],
        )
        if not result.failed:
            self.refresh_report()

        return not result.failed

    def bind_tpm2(self) -> bool:
        """Bind pool to TPM2.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.bind_tpm2()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='bind tpm2',
            positional_args=[self.name],
        )
        if not result.failed:
            self.refresh_report()

        return not result.failed

    def rebind_keyring(self, key_desc: str) -> bool:
        """Rebind pool to keyring.

        Args:
            key_desc: Key description

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.rebind_keyring('mykey')
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='rebind keyring',
            positional_args=[self.name, key_desc],
        )

        if not result.failed:
            self.refresh_report()

        return not result.failed

    def rebind_clevis(self) -> bool:
        """Rebind pool to Clevis.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.rebind_clevis()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='rebind clevis',
            positional_args=[self.name],
        )

        if not result.failed:
            self.refresh_report()

        return not result.failed

    def unbind_keyring(self) -> bool:
        """Unbind pool from keyring.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.unbind_keyring()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='unbind keyring',
            positional_args=[self.name],
        )
        if not result.failed:
            self.refresh_report()

        return not result.failed

    def unbind_clevis(self) -> bool:
        """Unbind pool from Clevis.

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pool.unbind_clevis()
            True
            ```
        """
        if not self.name:
            logging.error('Pool name required')
            return False

        result = self.run_command(
            subcommand='pool',
            action='unbind clevis',
            positional_args=[self.name],
        )
        if not result.failed:
            self.refresh_report()

        return not result.failed

    @classmethod
    def from_report(cls, report: PoolReport) -> StratisPool | None:
        """Create pool from report.

        Args:
            report: Pool report data

        Returns:
            StratisPool instance or None if invalid

        Example:
            ```python
            pool = StratisPool.from_report(report)
            ```
        """
        if not report.name:
            return None

        # Get paths from report
        paths = report.get_device_paths()

        # Create pool with report already attached
        return cls(
            name=report.name,
            uuid=report.uuid,
            encryption=report.encryption,
            blockdevs=paths,
            report=report,  # Attach the report directly
        )

    @classmethod
    def get_all(cls) -> list[StratisPool]:
        """Get all Stratis pools.

        Returns:
            List of StratisPool instances

        Example:
            ```python
            StratisPool.get_all()
            [StratisPool(name='pool1', ...), StratisPool(name='pool2', ...)]
            ```
        """
        pools: list[StratisPool] = []

        # Get all reports
        reports = PoolReport.get_all()

        # Create pools from reports
        pools.extend(pool for report in reports if (pool := cls.from_report(report)))

        return pools

    @classmethod
    def setup_blockdevices(cls) -> list[str]:
        """Set up block devices for testing.

        Returns:
            List of device paths

        Example:
            ```python
            StratisPool.setup_blockdevices()
            ['/dev/sda', '/dev/sdb']
            ```
        """
        # Get free disks
        blockdevices = get_free_disks()
        if not blockdevices:
            pytest.skip('No free disks found')

        # Group disks by block sizes
        filtered_disks_by_block_sizes: dict[tuple[int, int], list[str]] = {}
        for disk in blockdevices:
            block_sizes = (disk.sector_size, disk.block_size)
            if block_sizes in filtered_disks_by_block_sizes:
                filtered_disks_by_block_sizes[block_sizes].append(str(disk.path))
            else:
                filtered_disks_by_block_sizes[block_sizes] = [str(disk.path)]

        # Find devices with the most common block sizes
        most_common_block_sizes: list[str] = []
        for disks in filtered_disks_by_block_sizes.values():
            if len(disks) > len(most_common_block_sizes):
                most_common_block_sizes = disks

        # Clear start of devices
        for disk in most_common_block_sizes:
            run(f'dd if=/dev/zero of={disk} bs=1M count=10')

        return most_common_block_sizes
