# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Snapshot set management.

This module provides functionality for managing Snapshot Sets:
- Snapset creation and deletion
- Snapset activation and deactivation
- Snapset reverting and resizing
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from sts.snapm.base import SnapmBase, SnapmOptions
from sts.snapm.snapshot import SnapshotInfo

if TYPE_CHECKING:
    from sts.utils.cmdline import CommandResult


@dataclass
class SnapsetInfo:
    """Snapset information.

    Contains metadata about a snapset:
    - Basic identification (name, UUID)
    - Source and mount point lists
    - Snapshot count and timestamp
    - Status and boot configuration
    - Member snapshots information

    Args:
        name: Snapset name (optional)
        sources: List of source paths (optional)
        mount_points: List of mount points (optional)
        devices: List of device paths (optional)
        snapshot_count: Number of snapshots in set (optional)
        timestamp: Creation unix timestamp (optional)
        time: Human-readable creation time (optional)
        uuid: Snapset UUID (optional)
        status: Current status (optional)
        autoactivate: Autoactivation status (boolean) (optional)
        bootable: Whether snapset has boot entry (boolean) (optional)
        boot_entries: Dictionary with boot entry IDs (optional)
        snapshots: List of member snapshot information (optional)
    """

    name: str | None = None
    sources: list[str] = field(default_factory=list)
    mount_points: list[str] = field(default_factory=list)
    devices: list[str] = field(default_factory=list)
    snapshot_count: int | None = None
    timestamp: int | None = None
    time: str | None = None
    uuid: str | None = None
    status: str | None = None
    autoactivate: bool | None = None
    bootable: bool | None = None
    boot_entries: dict[str, str] = field(default_factory=dict)
    snapshots: list[SnapshotInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SnapsetInfo:
        """Create snapset info from dictionary.

        Args:
            data: Dictionary data from snapm report

        Returns:
            SnapsetInfo instance
        """
        # Handle lists with proper defaults
        sources = data.get('Sources', []) if isinstance(data.get('Sources'), list) else []
        mount_points = data.get('MountPoints', []) if isinstance(data.get('MountPoints'), list) else []
        devices = data.get('Devices', []) if isinstance(data.get('Devices'), list) else []

        # Handle boot entries dictionary
        boot_entries = data.get('BootEntries', {}) if isinstance(data.get('BootEntries'), dict) else {}

        # Parse member snapshots if available
        snapshots = []
        if isinstance(data.get('Snapshots'), list):
            snapshots = [SnapshotInfo.from_dict(snapshot_data) for snapshot_data in data.get('Snapshots', [])]

        return cls(
            name=data.get('SnapsetName'),
            sources=sources,
            mount_points=mount_points,
            devices=devices,
            snapshot_count=data.get('NrSnapshots'),
            timestamp=data.get('Timestamp'),
            time=data.get('Time'),
            uuid=data.get('UUID'),
            status=data.get('Status'),
            autoactivate=data.get('Autoactivate'),
            bootable=data.get('Bootable'),
            boot_entries=boot_entries,
            snapshots=snapshots,
        )


@dataclass
class Snapset(SnapmBase):
    """Snapset management.

    A Snapset is a collection of snapshots across multiple filesystems.
    This class provides operations for managing snapsets:
    - Creating and deleting snapsets
    - Activating and deactivating snapsets
    - Renaming snapsets
    - Reverting to snapshots
    - Listing and displaying snapset information

    Args:
        name: Snapset name (optional, discovered from system)
        uuid: Snapset UUID (optional, discovered from system)
        id: Snapset ID (optional, discovered from system)
        debugopts: Debug options to pass to snapm commands
        verbose: Whether to enable verbose output
        info: Detailed snapset information (optional, discovered from system)

    Examples:
        Create a snapset:
        snapset = Snapset()
        snapset.create('my_snapset', ['/mnt/fs1', '/mnt/fs2'])

        Use an existing snapset:
        snapset = Snapset(name='my_snapset')

        Delete a snapset:
        snapset = Snapset(name='my_snapset')
        snapset.delete()
    """

    SUBCOMMAND: ClassVar[str] = 'snapset'

    name: str | None = None
    uuid: str | None = None
    info: SnapsetInfo | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize snapset.

        Performs additional setup:
        - Calls parent initialization
        - Discovers snapset information if identifiers provided
        """
        # Discover snapset info if any identifier is provided
        if self.name or self.uuid:
            self.refresh_info()

    def refresh_info(self) -> bool:
        """Refresh snapset information.

        Retrieves detailed information about the snapset:
        - Updates snapset attributes
        - Gets snapshot list and member information
        - Checks status

        Returns:
            True if successful, False otherwise

        Note:
            Logs an error message if no snapset identifier is available or if the operation fails
        """
        result = self.show()

        if result.failed:
            logging.error(f'Failed to get snapset info: {result.stderr}')
            return False

        if not result.stdout:
            return False

        try:
            data_raw: list[dict[str, Any]] = json.loads(result.stdout)

            data: dict[str, Any]
            if not data_raw:
                logging.error(f'Failed to get snapshot info: {result.stderr}')
                return False
            data = data_raw[0]

            # Create or update info
            self.info = SnapsetInfo.from_dict(data)

        except json.JSONDecodeError as e:
            logging.warning(f'Failed to parse snapset info (invalid JSON): {e}')
            return False
        except (KeyError, TypeError) as e:
            logging.warning(f'Failed to process snapset info (unexpected format): {e}')
            return False

        return True

    def _common_operation(
        self, action: str, options: SnapmOptions | None = None, positional_args: list[str] | None = None
    ) -> bool:
        """Common method for shared operations.

        Handles operations that follow the same parameter pattern:
        - Uses stored attributes (name, UUID, or ID)
        - Executes the specified action
        - Updates information if successful

        Args:
            action: Operation to perform
            options: Additional options to include in the command

        Returns:
            True if successful, False otherwise
        """
        if not options:
            options = {}
        if not positional_args:
            positional_args = []

        # Use stored attributes
        if self.name:
            options['--name'] = self.name
        elif self.uuid:
            options['--uuid'] = self.uuid
        else:
            logging.error('No snapset identifier available')
            return False

        result = self.run_command(
            subcommand=self.SUBCOMMAND, action=action, options=options, positional_args=positional_args
        )

        if not result.failed:
            # Refresh information
            if action != 'delete':
                self.refresh_info()
            return True

        return False

    def create(
        self,
        snapset_name: str | None = None,
        sources: list[str] | None = None,
        size_policy: str | None = None,
        *,
        bootable: bool = False,
        revert: bool = False,
    ) -> bool | CommandResult:
        """Create a snapset.

        Creates a new snapset that includes the specified sources:
        - Snapset name must be unique
        - Sources must be valid mount points or block devices
        - Creates a snapshot of each source's current state
        - Optional boot and revert entries
        - Optional size policy controls snapshot space allocation

        Args:
            snapset_name: Name for the new snapset (uses self.name if not provided)
            sources: List of sources to include in snapset. Each source can be one of:
                    - A plain path: '/mnt/data'
                    - A path with size policy: '/mnt/data:2G' or '/mnt/data:50%FREE'
            bootable: Whether to create a boot entry for this snapset
            revert: Whether to create a revert entry for this snapset
            size_policy: Default size policy for all sources (e.g. "50%FREE", "2G")

        Returns:
            True if successful, False otherwise

        Note:
            Logs an error message if the operation fails

        Example:
            ```python
            # Using instance attribute
            snapset = Snapset(name='backup_1')
            snapset.create(sources=['/mnt/data', '/mnt/home'])

            # With bootable option
            snapset = Snapset()
            snapset.create('backup_1', ['/mnt/data', '/mnt/home'], bootable=True)

            # With size policy
            snapset = Snapset()
            snapset.create('backup_1', ['/mnt/data', '/mnt/home:2G', '/var:50%FREE'], size_policy='25%FREE')
            ```
        """
        # Use instance name if not provided
        name = snapset_name or self.name
        if not name:
            logging.error('Snapset name required')
            return False

        # Ensure sources is a list
        if sources is None:
            logging.error('Sources required')
            return False

        options: SnapmOptions = {}
        if bootable:
            options['--bootable'] = None
        if revert:
            options['--revert'] = None
        if size_policy:
            options['--size-policy'] = size_policy

        # Add sources to positional args
        positional_args = [name]
        positional_args.extend(sources)

        result = self.run_command(
            subcommand=self.SUBCOMMAND, action='create', options=options, positional_args=positional_args
        )

        if not result.failed:
            # Update instance attributes
            self.name = name
            return self.refresh_info()

        error_message = f'Failed to create snapset: {result.stderr}'
        logging.error(error_message)
        return False

    def delete(self) -> bool:
        """Delete a snapset.

        Removes a snapset and all associated snapshots:
        - Uses stored attributes (name, UUID, or ID) or provided snapset_name
        - Snapset must exist
        - Cannot be undone

        Returns:
            True if successful, False otherwise

        Note:
            Logs an error message if no snapset identifier is available or if the operation fails

        Example:
            ```python
            # Using instance attributes
            snapset = Snapset(name='backup_1')
            snapset.delete()
            ```
        """
        return self._common_operation('delete')

    def rename(self, new_name: str) -> bool:
        """Rename a snapset.

        Changes the name of an existing snapset:
        - Uses stored name
        - New name must not exist
        - Preserves all snapshots and configurations

        Args:
            new_name: New snapset name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            snapset.rename('daily_backup')
            ```
        """
        if not self.name:
            logging.error('Current snapset name required')
            return False

        result = self.run_command(subcommand=self.SUBCOMMAND, action='rename', positional_args=[self.name, new_name])

        if not result.failed:
            # Update instance name
            self.name = new_name
            self.refresh_info()
            return True

        return False

    def revert(self) -> bool:
        """Revert to snapset.

        Rolls back to the state captured in the snapset:
        - Uses stored attributes (name, UUID, or ID)
        - Snapset must exist
        - Potentially destructive - replaces current data with snapshot data
        - May need system reboot to complete

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            snapset.revert()
            ```
        """
        return self._common_operation('revert')

    def resize(self, sources: list[str] | None = None, size_policy: str | None = None) -> bool:
        """Resize snapset.

        Adjusts the size allocation for snapshots in the set:
        - Uses stored attributes (name, UUID, or ID)
        - Can specify new size policies for specific sources
        - Can apply default size policy to all sources

        Args:
            sources: List of sources with optional size policies (e.g. ['/path:2G'])
            size_policy: Default size policy to apply (e.g. "25%FREE")

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Resize specific sources
            snapset = Snapset(name='backup_1')
            snapset.resize(['/mnt/data:4G', '/var:50%FREE'])

            # Apply default policy to all sources
            snapset = Snapset(name='backup_1')
            snapset.resize(size_policy='25%FREE')
            ```
        """
        options: SnapmOptions = {}
        positional_args: list[str] = []

        if size_policy:
            options['--size-policy'] = size_policy

        # Add sources if provided
        if sources:
            positional_args.extend(sources)

        result = self._common_operation('resize', options=options, positional_args=positional_args)

        if not result:
            logging.error('Failed to resize snapset')

        return result

    def activate(self) -> bool:
        """Activate a snapset.

        Makes the snapset's snapshots active:
        - Uses stored attributes (name, UUID, or ID)
        - Snapset must exist
        - May mount filesystems

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            snapset.activate()
            ```
        """
        return self._common_operation('activate')

    def deactivate(self) -> bool:
        """Deactivate a snapset.

        Makes the snapset's snapshots inactive:
        - Uses stored attributes (name, UUID, or ID)
        - Snapset must exist
        - May unmount filesystems

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            snapset.deactivate()
            ```
        """
        return self._common_operation('deactivate')

    def autoactivate(self, *, enable: bool = True) -> bool:
        """Enable or disable auto-activation for a snapset.

        Configures snapset to activate automatically:
        - Uses stored attributes (name, UUID, or ID)
        - Snapset must exist
        - Takes effect at system boot

        Args:
            enable: Whether to enable (True) or disable (False) autoactivation

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            snapset.autoactivate(True)  # Enable autoactivation
            snapset.autoactivate(False)  # Disable autoactivation
            ```
        """
        options: SnapmOptions = {}

        # Add yes/no option
        if enable:
            options['--yes'] = None
        else:
            options['--no'] = None

        operation = 'enable' if enable else 'disable'
        result = self._common_operation('autoactivate', options)

        if not result:
            logging.error(f'Failed to {operation} snapshot autoactivation')

        return result

    def list(self, *, fields: str | None = None, json_output: bool = False) -> CommandResult:
        """List all snapsets.

        Lists available snapsets:
        - Shows basic information
        - Can select custom fields
        - Optional JSON output

        Args:
            fields: Comma-separated list of fields to display
            json_output: Whether to output in JSON format

        Returns:
            Command result with list output

        Example:
            ```python
            # Simple list
            snapset = Snapset()
            result = snapset.list()
            print(result.stdout)

            # Custom fields
            result = snapset.list('name,uuid,status')

            # JSON output
            result = snapset.list(json_output=True)
            ```
        """
        options: SnapmOptions = {}

        # Add name/uuid if set in this instance
        if self.name:
            options['--name'] = self.name
        elif self.uuid:
            options['--uuid'] = self.uuid

        # Add fields if provided
        if fields:
            options['--options'] = fields

        # Add JSON output if requested
        if json_output:
            options['--json'] = None

        return self.run_command(subcommand=self.SUBCOMMAND, action='list', options=options)

    def show(self, *, include_members: bool = True, json_output: bool = True) -> CommandResult:
        """Show detailed snapset information.

        Displays comprehensive snapset details:
        - Uses stored attributes (name, UUID, or ID)
        - Shows all snapshots if requested (enabled by default)
        - Displays configuration
        - Includes status information

        Args:
            include_members: Whether to include individual snapshots (default: True)
            json_output: Whether to output in JSON format (default: True)

        Returns:
            Command result with detailed information

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            result = snapset.show(include_members=True)
            print(result.stdout)
            ```
        """
        options: SnapmOptions = {}

        # Use stored attributes
        if self.name:
            options['--name'] = self.name
        elif self.uuid:
            options['--uuid'] = self.uuid
        else:
            logging.error('No snapset identifier available')
            return self.run_command(subcommand=self.SUBCOMMAND, action='show')

        # Add member and json options
        if include_members:
            options['--members'] = None

        if json_output:
            options['--json'] = None

        return self.run_command(subcommand=self.SUBCOMMAND, action='show', options=options)

    def prune(self, sources: list[str] | None = None) -> bool:
        """Prunes sources from a snapset.

        Removes specified sources (and their snapshots) from the snapset:
        - Uses stored attributes (name, UUID, or ID)
        - Snapset must exist
        - Removes snapshots for the specified sources
        - Remaining snapshots in the snapset are preserved
        - Cannot be undone - snapshots are permanently removed

        Args:
            sources: List of source paths to remove from the snapset

        Returns:
            True if successful, False otherwise

        Note:
            - Logs an error message if the operation fails
            - Pruned snapshots cannot be recovered
            - Snapset must exist and be accessible

        Example:
            ```python
            # Prune specific sources from snapset
            snapset = Snapset(name='backup_1')
            snapset.prune(['/mnt/data', '/mnt/temp'])
            ```
        """
        positional_args: list[str] = []

        if self.name:
            positional_args.append(self.name)
        if sources:
            positional_args.extend(sources)

        result = self.run_command(subcommand=self.SUBCOMMAND, action='prune', positional_args=positional_args)

        if not result.succeeded:
            logging.warning('Failed to prune snapset')
        self.refresh_info()
        return result.succeeded

    def split(self, new_name: str | None = None, sources: list[str] | None = None) -> Snapset:
        """Split a snapset into a new snapset.

        Creates a new snapset by splitting the current snapset:
        - Moves specified snapshots from this snapset to a new snapset
        - Original snapset remains with remaining snapshots
        - New snapset gets the specified name

        Args:
            new_name: Name for the new snapset
            sources: List of sources to move to the new snapset

        Returns:
            New Snapset instance containing the split snapshots

        Note:
            - Original snapset is updated to reflect the remaining snapshots
            - New snapset name must be unique
            - Logs an error message if the operation fails

        Example:
            ```python
            # Split specific sources into new snapset
            snapset = Snapset(name='backup_full')
            new_snapset = snapset.split('backup_partial', ['/mnt/data', '/mnt/home'])
            ```
        """
        positional_args: list[str] = [self.name or '']

        # Add sources if provided
        if new_name:
            positional_args.append(new_name)
        if sources:
            positional_args.extend(sources)

        result = self.run_command(subcommand=self.SUBCOMMAND, action='split', positional_args=positional_args)

        if not result:
            logging.error('Failed to split snapset')
            return Snapset()
        self.refresh_info()
        return Snapset(name=new_name)

    @classmethod
    def get_all(cls) -> list[Snapset]:
        """Get all snapsets.

        Retrieves information about all snapsets:
        - Lists all snapsets in system
        - Creates instances with attributes
        - May be filtered later

        Returns:
            List of Snapset instances

        Example:
            ```python
            snapsets = Snapset.get_all()
            for snapset in snapsets:
                print(snapset.name)
                if snapset.info and snapset.info.snapshots:
                    print(f'  Contains {len(snapset.info.snapshots)} snapshots:')
                    for snapshot in snapset.info.snapshots:
                        print(f'    - {snapshot.name} ({snapshot.status})')
            ```
        """
        snapsets: list[Snapset] = []

        # Create base instance to run command
        base = cls()

        # Get snapset with members in JSON format for easier parsing
        options = {'--json': None, '--members': None}
        result = base.run_command(subcommand=cls.SUBCOMMAND, action='show', options=options)

        if result.failed or not result.stdout:
            return snapsets

        try:
            # Parse JSON output
            data = json.loads(result.stdout)

            # Handle different possible JSON structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'snapsets' in data:
                items = data['snapsets']
            else:
                items = [data]

            # Create snapset instances from each entry
            for item in items:
                snapset = cls()

                # Set basic attributes
                if 'SnapsetName' in item:
                    snapset.name = item['SnapsetName']
                if 'UUID' in item:
                    snapset.uuid = item['UUID']

                # Create info object
                snapset.info = SnapsetInfo.from_dict(item)

                snapsets.append(snapset)

        except (json.JSONDecodeError, TypeError) as e:
            logging.warning(f'Failed to parse snapsets: {e}')

        return snapsets

    def get_snapshots(self) -> list[SnapshotInfo]:
        """Get all snapshots in this snapset.

        Returns:
            List of SnapshotInfo objects for all snapshots in this snapset

        Example:
            ```python
            snapset = Snapset(name='backup_1')
            for snapshot in snapset.get_snapshots():
                print(f'{snapshot.name}: {snapshot.status}')
                print(f'  Source: {snapshot.source}, Mount point: {snapshot.mount_point}')
                print(f'  Size: {snapshot.size}, Free: {snapshot.free}')
            ```
        """
        # Refresh info to ensure we have the latest data including snapshots
        if not self.refresh_info():
            return []

        # Return snapshots from info if available
        if self.info and self.info.snapshots:
            return self.info.snapshots

        return []
