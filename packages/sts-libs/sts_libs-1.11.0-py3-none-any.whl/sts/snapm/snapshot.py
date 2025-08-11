# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Snapshot management.

This module provides functionality for managing individual snapshots:
- Snapshot activation and deactivation
- Auto-activation configuration
- Information gathering
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from sts.snapm.base import SnapmBase, SnapmOptions

if TYPE_CHECKING:
    from sts.utils.cmdline import CommandResult


@dataclass
class SnapshotInfo:
    """Snapshot information.

    Contains metadata about a snapshot:
    - Basic identification (name)
    - Associated snapset info
    - Status information
    - Size information
    - Device details

    Args:
        name: Snapshot name (optional)
        snapset_name: Parent snapset name (optional)
        origin: Origin device path (optional)
        timestamp: Creation unix timestamp (optional)
        time: Human-readable creation time (optional)
        source: Source path (optional)
        mount_point: Mount point path (optional)
        provider: Snapshot provider plugin name (optional)
        uuid: Snapshot UUID (optional)
        status: Current status (e.g., "Active") (optional)
        size: Human-readable snapshot size (e.g., "10.3GiB") (optional)
        free: Human-readable free space (e.g., "10.3GiB") (optional)
        size_bytes: Size in bytes (optional)
        free_bytes: Free space in bytes (optional)
        autoactivate: Autoactivation status (boolean) (optional)
        device_path: Full device path (optional)
    """

    name: str | None = None
    snapset_name: str | None = None
    origin: str | None = None
    timestamp: int | None = None
    time: str | None = None
    source: str | None = None
    mount_point: str | None = None
    provider: str | None = None
    uuid: str | None = None
    status: str | None = None
    size: str | None = None
    free: str | None = None
    size_bytes: int | None = None
    free_bytes: int | None = None
    autoactivate: bool | None = None
    device_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SnapshotInfo:
        """Create snapshot info from dictionary.

        Args:
            data: Dictionary data from snapm report

        Returns:
            SnapshotInfo instance
        """
        return cls(
            name=data.get('Name'),
            snapset_name=data.get('SnapsetName'),
            origin=data.get('Origin'),
            timestamp=data.get('Timestamp'),
            time=data.get('Time'),
            source=data.get('Source'),
            mount_point=data.get('MountPoint'),
            provider=data.get('Provider'),
            uuid=data.get('UUID'),
            status=data.get('Status'),
            size=data.get('Size'),
            free=data.get('Free'),
            size_bytes=data.get('SizeBytes'),
            free_bytes=data.get('FreeBytes'),
            autoactivate=data.get('Autoactivate'),
            device_path=data.get('DevicePath'),
        )


@dataclass
class Snapshot(SnapmBase):
    """Snapshot management.

    A Snapshot is a point-in-time copy of a filesystem.
    This class provides operations for managing individual snapshots:
    - Activating and deactivating snapshots
    - Configuring automatic activation
    - Listing and displaying snapshot information

    Args:
        id: Snapshot ID (optional, discovered from system)
        snapset_name: Parent snapset name (optional, discovered from system)
        snapset_uuid: Parent snapset UUID (optional, discovered from system)
        debugopts: Debug options to pass to snapm commands
        verbose: Whether to enable verbose output
        info: Detailed snapshot information (optional, discovered from system)

    Examples:
        Activate a snapshot:
        snapshot = Snapshot(snapset_name='my_snapset')
        snapshot.activate()

        Show snapshot details using ID:
        snapshot = Snapshot(id='123')
        snapshot.show()
    """

    # Class-level constants
    SUBCOMMAND: ClassVar[str] = 'snapshot'

    # Instance attributes
    name: str | None = None
    uuid: str | None = None
    snapset_name: str | None = None
    snapset_uuid: str | None = None
    info: SnapshotInfo | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize snapshot.

        Performs additional setup:
        - Calls parent initialization
        - Discovers snapshot information if identifiers provided
        """
        # Discover snapshot info if any identifier is provided
        if self.name or self.uuid:
            self.refresh_info()

    def _build_identifier_options(self) -> SnapmOptions:
        """Build options dictionary with available identifiers.

        Returns:
            Options dictionary
        """
        options: SnapmOptions = {}

        if self.name:
            options['--snapshot-name'] = self.name
        elif self.uuid:
            options['--snapshot-uuid'] = self.uuid
        elif self.snapset_name:
            options['--name'] = self.snapset_name
        elif self.snapset_uuid:
            options['--uuid'] = self.snapset_uuid
        else:
            logging.warning('No snapshot identifier (ID, snapset name, or snapset UUID) available')

        return options

    def _common_operation(self, action: str, options: SnapmOptions | None = None) -> bool:
        """Common method for shared operations.

        Args:
            action: Operation to perform (e.g., "activate", "deactivate")
            options: Additional options to include in the command

        Returns:
            True if successful, False otherwise
        """
        if not options:
            options = {}
        positional_args: list[str] = []

        id_options = self._build_identifier_options()
        if not id_options:
            return False

        options.update(id_options)

        result = self.run_command(
            subcommand=self.SUBCOMMAND, action=action, options=options, positional_args=positional_args
        )

        if result.failed:
            logging.error(f'Failed to {action} snapshot: {result.stderr}')
            return False

        # Refresh information on success
        self.refresh_info()
        return True

    def refresh_info(self) -> bool:
        """Refresh snapshot information.

        Retrieves detailed information about the snapshot:
        - Updates snapshot attributes
        - Gets status

        Returns:
            True if successful, False otherwise

        Note:
            Logs an error message if no snapshot identifier is available or if the operation fails
        """
        # Get report
        options: SnapmOptions = {}

        # Add JSON output option for easier parsing
        options['--json'] = None

        # Ensure an identifier is available to refresh instance specific information
        if not self._build_identifier_options():
            return False

        result = self.show()

        if result.failed:
            logging.error(f'Failed to get snapshot info: {result.stderr}')
            return False

        if not result.stdout:
            return False

        try:
            data_raw: list[dict[str, Any]] = json.loads(result.stdout)
            if not data_raw:
                logging.error(f'Failed to get snapshot info: {result.stderr}')
                return False
            # Getting data for specific name or uuid, so we only need first index
            data: dict[str, Any] = data_raw[0]

            # Create or update info
            self.info = SnapshotInfo.from_dict(data)

        except json.JSONDecodeError as e:
            logging.warning(f'Failed to parse snapshot info (invalid JSON): {e}')
            return False
        except (KeyError, TypeError) as e:
            logging.warning(f'Failed to process snapshot info (unexpected format): {e}')
            return False

        return True

    def activate(self) -> bool:
        """Activate a snapshot.

        Makes a snapshot active:
        - Uses stored attributes (ID, snapset name, or snapset UUID)
        - Snapshot must exist
        - May mount filesystem

        Returns:
            True if successful, False otherwise

        Note:
            Logs an error message if no snapshot identifier is available or if the operation fails

        Example:
            ```python
            # Activate by ID
            snapshot = Snapshot(id='123')
            snapshot.activate()
            ```
        """
        return self._common_operation('activate')

    def deactivate(self) -> bool:
        """Deactivate a snapshot.

        Makes a snapshot inactive:
        - Uses stored attributes (ID, snapset name, or snapset UUID)
        - Snapshot must exist
        - May unmount filesystem

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            snapshot = Snapshot(snapset_name='backup_1')
            snapshot.deactivate()
            ```
        """
        return self._common_operation('deactivate')

    def autoactivate(self, *, enable: bool = True) -> bool:
        """Enable or disable auto-activation for a snapshot.

        Configures snapshot to activate automatically:
        - Uses stored attributes (ID, snapset name, or snapset UUID)
        - Snapshot must exist
        - Takes effect at system boot

        Args:
            enable: Whether to enable (True) or disable (False) autoactivation

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Enable autoactivation
            snapshot = Snapshot(id='123')
            snapshot.autoactivate(True)

            # Disable autoactivation
            snapshot = Snapshot(snapset_name='backup_1')
            snapshot.autoactivate(False)
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

    def list(self, fields: str | None = None, *, json_output: bool = False) -> CommandResult:
        """List all snapshots.

        Lists available snapshots:
        - Shows basic information
        - Can select custom fields
        - Optional JSON output
        - Can filter by snapset name or UUID

        Args:
            fields: Comma-separated list of fields to display
                   Example: "id,name,status,mount_point"
            json_output: Whether to output in JSON format

        Returns:
            Command result with list output

        Example:
            ```python
            # Simple list
            snapshot = Snapshot()
            result = snapshot.list()
            print(result.stdout)

            # Custom fields with JSON output
            snapshot = Snapshot(snapset_name='backup_1')
            result = snapshot.list(fields='name,origin,status', json_output=True)

            # Parse JSON output
            import json

            snapshots_data = json.loads(result.stdout)
            for snap in snapshots_data:
                print(f'{snap["name"]}: {snap["status"]}')
            ```
        """
        options: SnapmOptions = {}

        # No need to fail here. If ID is not available, empty dict is returned
        id_options = self._build_identifier_options()
        options.update(id_options)

        # Add fields if provided
        if fields:
            options['--options'] = fields

        # Add JSON output if requested
        if json_output:
            options['--json'] = None

        return self.run_command(subcommand=self.SUBCOMMAND, action='list', options=options)

    def show(self, *, json_output: bool = True) -> CommandResult:
        """Show detailed snapshot information.

        Displays comprehensive snapshot details:
        - Uses stored attributes (name, UUID, or ID)
        - Displays configuration
        - Includes status information

        Args:
            json_output: Whether to output in JSON format (default: True)

        Returns:
            Command result with detailed information

        Example:
            ```python
            snapset = Snapshot()
            result = snapset.show()
            print(result.stdout)
            ```
        """
        options: SnapmOptions = {}

        # No need to fail here. If ID is not available, empty dict is returned
        id_options = self._build_identifier_options()
        options.update(id_options)

        # Add json options

        if json_output:
            options['--json'] = None

        return self.run_command(subcommand=self.SUBCOMMAND, action='show', options=options)
