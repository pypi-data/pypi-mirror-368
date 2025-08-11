# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Stratis filesystem management.

This module provides functionality for managing Stratis filesystems:
- Filesystem creation and management
- Thin provisioning and size limits
- Snapshot creation and tracking
- Space usage monitoring

Key features:
- XFS as the default filesystem
- Copy-on-write snapshots
- Dynamic size management
- Origin tracking for snapshots
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from sts.stratis.base import StratisBase, StratisConfig, StratisOptions
from sts.utils.size import size_human_2_size_bytes


@dataclass
class FilesystemReport:
    """Filesystem report data.

    Contains filesystem metadata:
    - Basic information (name, UUID)
    - Size information (total, limit)
    - Snapshot details (origin)
    - Usage statistics

    Args:
        name: Filesystem name (optional, discovered from system)
        uuid: Filesystem UUID (optional, discovered from system)
        size: Filesystem size (optional, discovered from system)
        size_limit: Size limit (optional, discovered from system)
        origin: Origin filesystem for snapshots (optional)
        used: Used space (optional, discovered from system)

    Example:
        ```python
        report = FilesystemReport()  # Discovers first available filesystem
        report = FilesystemReport(name='fs1')  # Discovers other values
        ```
    """

    name: str | None = None
    uuid: str | None = None
    size: str | None = None  # Total size (e.g. "10 GiB")
    size_limit: str | None = None  # Maximum size allowed
    origin: str | None = None  # Source filesystem for snapshots
    used: str | None = None  # Space currently in use

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FilesystemReport | None:
        """Create report from dictionary.

        Parses stratis report format:
        - Handles missing fields
        - Validates data types
        - Reports parsing errors

        Args:
            data: Dictionary data from stratis report

        Returns:
            FilesystemReport instance or None if invalid
        """
        try:
            return cls(
                name=data.get('name'),
                uuid=data.get('uuid'),
                size=data.get('size'),
                size_limit=data.get('size_limit'),
                origin=data.get('origin'),
                used=data.get('used'),
            )
        except (KeyError, TypeError) as e:
            logging.warning(f'Invalid filesystem report data: {e}')
            return None


@dataclass
class StratisFilesystem(StratisBase):
    """Stratis filesystem representation.

    Manages filesystems with:
    - Thin provisioning
    - Snapshot capabilities
    - Size management
    - Usage tracking

    Args:
        name: Filesystem name (optional, discovered from system)
        pool_name: Pool name (optional, discovered from system)
        uuid: Filesystem UUID (optional, discovered from system)
        size: Filesystem size in bytes (optional, discovered from system)
        size_limit: Size limit (optional, discovered from system)
        origin: Origin filesystem for snapshots (optional)
        used: Used space (optional, discovered from system)

    Example:
        ```python
        fs = StratisFilesystem()  # Discovers first available filesystem
        fs = StratisFilesystem(name='fs1')  # Discovers other values
        ```
    """

    name: str | None = None
    pool_name: str | None = None
    uuid: str | None = None
    size: int | None = None  # Size in bytes
    size_limit: str | None = None  # Size limit (human readable)
    origin: str | None = None  # Source filesystem name
    used: str | None = None  # Used space (human readable)

    # Mount point base path
    FS_PATH: ClassVar[str] = '/stratis'

    def __post_init__(self) -> None:
        """Initialize filesystem.

        Discovery process:
        1. Initialize base class
        2. Find pool and filesystem info
        3. Parse size information
        4. Set filesystem attributes
        """
        # Initialize base class with default config
        super().__init__(config=StratisConfig())

        # Discover filesystem info if needed
        if not self.pool_name or not self.name:
            result = self.run_command('report')
            if result.succeeded and result.stdout:
                try:
                    report = json.loads(result.stdout)
                    for pool in report['pools']:
                        for fs in pool['filesystems']:
                            if not self.name or self.name == fs['name']:
                                # Set pool and filesystem names
                                if not self.pool_name:
                                    self.pool_name = pool['name']
                                if not self.name:
                                    self.name = fs['name']

                                # Parse size if available
                                if not self.size and 'size' in fs:
                                    size_bytes = size_human_2_size_bytes(fs['size'])
                                    if size_bytes is not None:
                                        self.size = int(size_bytes)

                                # Set other attributes
                                if not self.uuid:
                                    self.uuid = fs.get('uuid')
                                if not self.size_limit:
                                    self.size_limit = fs.get('size_limit')
                                if not self.origin:
                                    self.origin = fs.get('origin')
                                if not self.used:
                                    self.used = fs.get('used')
                                break
                        if self.name and self.pool_name:
                            break
                except (KeyError, ValueError) as e:
                    logging.warning(f'Failed to parse filesystem info: {e}')

    def get_fs_uuid(self) -> str | None:
        """Get filesystem UUID.

        Retrieves UUID from system:
        - Requires pool and filesystem names
        - UUID is stable across reboots
        - Used for unique identification

        Returns:
            Filesystem UUID or None if not found

        Example:
            ```python
            fs.get_fs_uuid()
            '123e4567-e89b-12d3-a456-426614174000'
            ```
        """
        if not self.pool_name or not self.name:
            return None

        result = self.run_command('report')
        if result.failed or not result.stdout:
            return None

        try:
            report = json.loads(result.stdout)
            for pool in report['pools']:
                if self.pool_name != pool['name']:
                    continue
                for fs in pool['filesystems']:
                    if self.name != fs['name']:
                        continue
                    return fs['uuid']
        except (KeyError, ValueError) as e:
            logging.warning(f'Failed to get filesystem UUID: {e}')

        return None

    def create(self, size: str | None = None, size_limit: str | None = None) -> bool:
        """Create filesystem.

        Creates filesystem with:
        - Optional initial size
        - Optional size limit
        - Thin provisioning enabled
        - Default mount options

        Args:
            size: Initial size (e.g. "10G")
            size_limit: Size limit (e.g. "20G")

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            fs.create(size='10G', size_limit='20G')
            True
            ```
        """
        if not self.pool_name or not self.name:
            logging.error('Pool name and filesystem name required')
            return False

        options: StratisOptions = {}
        if size:
            options['--size'] = size
        if size_limit:
            options['--size-limit'] = size_limit

        result = self.run_command(
            subcommand='filesystem',
            action='create',
            options=options,
            positional_args=[self.pool_name, self.name],
        )
        return not result.failed

    def destroy(self) -> bool:
        """Destroy filesystem.

        Removes filesystem:
        - Unmounts if mounted
        - Removes from pool
        - Deletes all data
        - Cannot be undone

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            fs.destroy()
            True
            ```
        """
        if not self.pool_name or not self.name:
            logging.error('Pool name and filesystem name required')
            return False

        result = self.run_command(
            subcommand='filesystem',
            action='destroy',
            positional_args=[self.pool_name, self.name],
        )
        return not result.failed

    def rename(self, new_name: str) -> bool:
        """Rename filesystem.

        Changes filesystem name:
        - Updates mount points
        - Preserves data and settings
        - Updates snapshot references

        Args:
            new_name: New filesystem name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            fs.rename('fs2')
            True
            ```
        """
        if not self.pool_name or not self.name:
            logging.error('Pool name and filesystem name required')
            return False

        result = self.run_command(
            subcommand='filesystem',
            action='rename',
            positional_args=[self.pool_name, self.name, new_name],
        )
        if not result.failed:
            self.name = new_name
        return not result.failed

    def snapshot(self, snapshot_name: str) -> StratisFilesystem | None:
        """Create filesystem snapshot.

        Creates copy-on-write snapshot:
        - Instant creation
        - Space-efficient
        - Tracks origin
        - Writable by default

        Args:
            snapshot_name: Snapshot name

        Returns:
            New filesystem instance or None if failed

        Example:
            ```python
            fs.snapshot('snap1')
            StratisFilesystem(name='snap1', ...)
            ```
        """
        if not self.pool_name or not self.name:
            logging.error('Pool name and filesystem name required')
            return None

        result = self.run_command(
            subcommand='filesystem',
            action='snapshot',
            positional_args=[self.pool_name, self.name, snapshot_name],
        )
        if result.failed:
            return None

        return StratisFilesystem(
            name=snapshot_name,
            pool_name=self.pool_name,
            size=self.size,
            origin=self.name,
        )

    def set_size_limit(self, limit: str) -> bool:
        """Set filesystem size limit.

        Limits filesystem growth:
        - Thin provisioning still active
        - Prevents space exhaustion
        - Can be changed later
        - Uses human-readable sizes

        Args:
            limit: Size limit (e.g. "20G")

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            fs.set_size_limit('20G')
            True
            ```
        """
        if not self.pool_name or not self.name:
            logging.error('Pool name and filesystem name required')
            return False

        result = self.run_command(
            subcommand='filesystem',
            action='set-size-limit',
            positional_args=[self.pool_name, self.name, limit],
        )
        if not result.failed:
            self.size_limit = limit
        return not result.failed

    def unset_size_limit(self) -> bool:
        """Unset filesystem size limit.

        Removes growth limit:
        - Allows unlimited growth
        - Limited only by pool size
        - Cannot be undone (must set new limit)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            fs.unset_size_limit()
            True
            ```
        """
        if not self.pool_name or not self.name:
            logging.error('Pool name and filesystem name required')
            return False

        result = self.run_command(
            subcommand='filesystem',
            action='unset-size-limit',
            positional_args=[self.pool_name, self.name],
        )
        if not result.failed:
            self.size_limit = None
        return not result.failed

    @classmethod
    def from_report(cls, report: FilesystemReport, pool_name: str) -> StratisFilesystem | None:
        """Create filesystem from report.

        Parses report data:
        - Validates required fields
        - Converts size formats
        - Sets relationships

        Args:
            report: Filesystem report data
            pool_name: Pool name

        Returns:
            StratisFilesystem instance or None if invalid

        Example:
            ```python
            fs = StratisFilesystem.from_report(report, 'pool1')
            ```
        """
        if not report.name:
            return None

        size_bytes = None
        if report.size:
            size_bytes = size_human_2_size_bytes(report.size)
            if size_bytes is None:
                logging.warning(f'Invalid size: {report.size}, using None')

        return cls(
            name=report.name,
            pool_name=pool_name,
            size=int(size_bytes) if size_bytes is not None else None,
            uuid=report.uuid,
            size_limit=report.size_limit,
            origin=report.origin,
            used=report.used,
        )

    @classmethod
    def get_all(cls, pool_name: str | None = None) -> list[StratisFilesystem]:
        """Get all Stratis filesystems.

        Lists filesystems:
        - Optionally filtered by pool
        - Includes snapshots
        - Provides full details
        - Sorted by pool

        Args:
            pool_name: Filter by pool name

        Returns:
            List of StratisFilesystem instances

        Example:
            ```python
            StratisFilesystem.get_all('pool1')
            [StratisFilesystem(name='fs1', ...), StratisFilesystem(name='fs2', ...)]
            ```
        """
        filesystems: list[StratisFilesystem] = []
        # Create base instance without __post_init__
        base = super().__new__(cls)
        StratisBase.__init__(base, config=StratisConfig())

        result = base.run_command('report')
        if result.failed or not result.stdout:
            return filesystems

        try:
            report = json.loads(result.stdout)
            for pool_data in report['pools']:
                current_pool = pool_data.get('name')
                if not current_pool:
                    logging.warning('Pool missing name')
                    continue
                if pool_name and pool_name != current_pool:
                    continue
                filesystems.extend(
                    [
                        fs
                        for fs_data in pool_data.get('filesystems', [])
                        if (
                            fs := cls.from_report(
                                FilesystemReport.from_dict(fs_data) or FilesystemReport(), current_pool
                            )
                        )
                    ]
                )
        except (KeyError, ValueError) as e:
            logging.warning(f'Failed to parse report: {e}')

        return filesystems
