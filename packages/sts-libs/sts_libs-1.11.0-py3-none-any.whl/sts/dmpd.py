# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Device mapper persistent data tools.

This module provides functionality for device-mapper-persistent-data tools:
- Cache tools (cache_check, cache_dump, etc.)
- Thin provisioning tools (thin_check, thin_dump, etc.)
- Metadata repair and restore

Device Mapper Persistent Data:
- Manages metadata for advanced DM targets
- Ensures data consistency across reboots
- Provides tools for metadata maintenance
- Supports metadata backup and restore
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict, cast

from sts.utils.cmdline import format_args, run
from sts.utils.packages import Dnf

if TYPE_CHECKING:
    from collections.abc import Mapping


class DmpdOptions(TypedDict, total=False):
    """Device mapper persistent data tool options.

    Common options for metadata tools:
    - quiet: Suppress output messages
    - super_block_only: Only check superblock integrity
    - skip_mappings: Skip block mapping verification
    - output: Output file for dumps/repairs
    - input: Input file for restores/repairs
    - repair: Attempt metadata repair
    - format: Output format (xml, human readable)
    - metadata_snap: Use metadata snapshot for consistency
    """

    quiet: str | None
    super_block_only: str | None
    skip_mappings: str | None
    output: str
    input: str
    repair: str | None
    format: str
    metadata_snap: str | None


def get_device_path(vg_name: str, lv_name: str) -> str:
    """Get device mapper path.

    Constructs device mapper path from VG/LV names:
    /dev/mapper/<vg_name>-<lv_name>

    Args:
        vg_name: Volume group name
        lv_name: Logical volume name

    Returns:
        Device mapper path
    """
    return f'/dev/mapper/{vg_name}-{lv_name}'


@dataclass
class DeviceSource:
    """Device source configuration.

    Represents a device that can be:
    - A regular file (metadata dump)
    - A logical volume (active device)
    - A device mapper device

    Args:
        file: Source file path (for metadata files)
        vg: Volume group name (for logical volumes)
        lv: Logical volume name (for logical volumes)
    """

    file: str | None = None
    vg: str | None = None
    lv: str | None = None

    def get_path(self) -> str | None:
        """Get device path.

        Returns path based on configuration:
        - File path if file is specified
        - Device mapper path if VG/LV specified
        - None if invalid configuration

        Returns:
            Device path or None if invalid configuration

        Example:
            ```python
            source = DeviceSource(file='/path/to/file')
            source.get_path()
            '/path/to/file'
            source = DeviceSource(vg='vg0', lv='lv0')
            source.get_path()
            '/dev/mapper/vg0-lv0'
            ```
        """
        if self.file:
            return self.file
        if self.vg and self.lv:
            return get_device_path(self.vg, self.lv)
        return None


class DeviceMapperPD:
    """Device mapper persistent data tools.

    Provides tools for managing metadata:
    - Cache metadata (dm-cache)
    - Thin pool metadata (dm-thin)
    - Metadata validation
    - Metadata repair
    - Backup/restore

    Key operations:
    1. Validation (check)
    2. Backup (dump)
    3. Repair (repair)
    4. Restore (restore)
    """

    # Available commands and their valid arguments
    # Each command supports specific subset of options
    COMMANDS: ClassVar[dict[str, set[str]]] = {
        'cache_check': {'quiet', 'super_block_only', 'skip_mappings'},
        'cache_dump': {'output', 'repair', 'format'},
        'cache_repair': {'input', 'output'},
        'cache_restore': {'input', 'output', 'quiet'},
        'thin_check': {'quiet', 'super_block_only', 'skip_mappings'},
        'thin_dump': {'output', 'repair', 'format', 'metadata_snap'},
        'thin_repair': {'input', 'output'},
        'thin_restore': {'input', 'output', 'quiet'},
    }

    def __init__(self) -> None:
        """Initialize device mapper tools.

        Ensures required tools are installed:
        - device-mapper-persistent-data package
        - Cache tools
        - Thin provisioning tools
        """
        # Install required package
        pm = Dnf()
        if not pm.install('device-mapper-persistent-data'):
            msg = 'Failed to install device-mapper-persistent-data'
            raise RuntimeError(msg)

    def _convert_options(self, options: Mapping[str, Any] | None) -> dict[str, str]:
        """Convert options to command arguments.

        Converts Python options to CLI format:
        - Filters None values
        - Converts values to strings
        - Preserves option order

        Args:
            options: Command options

        Returns:
            Command arguments
        """
        if not options:
            return {}
        return {k: str(v) for k, v in options.items() if v is not None}

    def _run(self, cmd: str, valid_args: set[str], options: Mapping[str, Any] | None = None) -> bool:
        """Run command with arguments.

        Executes command with validation:
        - Filters invalid arguments
        - Formats command string
        - Captures output and errors

        Args:
            cmd: Command to run
            valid_args: Valid arguments for command
            options: Command options

        Returns:
            True if successful, False otherwise
        """
        # Filter valid arguments
        args = {k: v for k, v in self._convert_options(options).items() if k in valid_args}

        # Build and run command
        cmd = f'{cmd} {format_args(**args)}'
        result = run(cmd)
        if result.failed:
            logging.error(f'Command failed: {cmd}')
            return False
        return True

    def _check_metadata(self, cmd: str, source: DeviceSource, options: DmpdOptions | None = None) -> bool:
        """Check metadata.

        Common metadata validation:
        - Validates source device
        - Runs appropriate check command
        - Handles command options

        Args:
            cmd: Command to run
            source: Source device
            options: Command options

        Returns:
            True if check passed, False otherwise
        """
        device = source.get_path()
        if not device:
            logging.error('Either source_file or source_vg/source_lv required')
            return False

        return self._run(f'{cmd} {device}', self.COMMANDS[cmd], options)

    def cache_check(self, source: DeviceSource, options: DmpdOptions | None = None) -> bool:
        """Check cache metadata.

        Validates dm-cache metadata:
        - Superblock integrity
        - Mapping correctness
        - Reference counts
        - Free space

        Args:
            source: Source device
            options: Command options

        Returns:
            True if check passed, False otherwise

        Example:
            ```python
            dmpd = DeviceMapperPD()
            source = DeviceSource(vg='vg0', lv='cache0')
            dmpd.cache_check(source, {'quiet': None})
            True
            ```
        """
        return self._check_metadata('cache_check', source, options)

    def thin_check(self, source: DeviceSource, options: DmpdOptions | None = None) -> bool:
        """Check thin metadata.

        Validates dm-thin metadata:
        - Superblock integrity
        - Device mappings
        - Space maps
        - Reference counts

        Args:
            source: Source device
            options: Command options

        Returns:
            True if check passed, False otherwise

        Example:
            ```python
            dmpd = DeviceMapperPD()
            source = DeviceSource(vg='vg0', lv='thin0')
            dmpd.thin_check(source, {'quiet': None})
            True
            ```
        """
        return self._check_metadata('thin_check', source, options)

    def thin_dump(self, source: DeviceSource, options: DmpdOptions | None = None) -> bool:
        """Dump thin metadata.

        Creates metadata backup:
        - XML or human readable format
        - Optional repair during dump
        - Can use metadata snapshot

        Args:
            source: Source device
            options: Command options

        Returns:
            True if dump succeeded, False otherwise

        Example:
            ```python
            dmpd = DeviceMapperPD()
            source = DeviceSource(vg='vg0', lv='thin0')
            dmpd.thin_dump(source, {'output': 'metadata.xml'})
            True
            ```
        """
        return self._check_metadata('thin_dump', source, options)

    def thin_restore(self, source_file: str | Path, target: DeviceSource, options: DmpdOptions | None = None) -> bool:
        """Restore thin metadata.

        Restores metadata from backup:
        - Validates input file
        - Creates new metadata
        - Preserves device mappings

        Args:
            source_file: Source metadata file
            target: Target device
            options: Command options

        Returns:
            True if restore succeeded, False otherwise

        Example:
            ```python
            dmpd = DeviceMapperPD()
            target = DeviceSource(vg='vg0', lv='thin0')
            dmpd.thin_restore('metadata.xml', target)
            True
            ```
        """
        source_path = Path(source_file)
        if not source_path.is_file():
            logging.error('Source file does not exist')
            return False

        target_path = target.get_path()
        if not target_path:
            logging.error('Either target_file or target_vg/target_lv required')
            return False

        restore_options = cast('dict[str, Any]', {'input': str(source_path), 'output': target_path})
        if options:
            restore_options.update(cast('dict[str, Any]', options))

        return self._run('thin_restore', self.COMMANDS['thin_restore'], restore_options)

    def thin_repair(self, source: DeviceSource, target: DeviceSource, options: DmpdOptions | None = None) -> bool:
        """Repair thin metadata.

        Attempts to repair corrupted metadata:
        - Reads corrupted metadata
        - Fixes inconsistencies
        - Creates repaired copy

        Args:
            source: Source device (corrupted)
            target: Target device (repaired)
            options: Command options

        Returns:
            True if repair succeeded, False otherwise

        Example:
            ```python
            dmpd = DeviceMapperPD()
            source = DeviceSource(vg='vg0', lv='thin0')
            target = DeviceSource(file='repaired.xml')
            dmpd.thin_repair(source, target)
            True
            ```
        """
        source_path = source.get_path()
        if not source_path:
            logging.error('Either source_file or source_vg/source_lv required')
            return False

        target_path = target.get_path()
        if not target_path:
            logging.error('Either target_file or target_vg/target_lv required')
            return False

        repair_options = cast('dict[str, Any]', {'input': source_path, 'output': target_path})
        if options:
            repair_options.update(cast('dict[str, Any]', options))

        return self._run('thin_repair', self.COMMANDS['thin_repair'], repair_options)
