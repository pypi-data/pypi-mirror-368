# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Boom boot entry management.

This module provides functionality for managing Boom boot entries:
- Entry creation and management
- Entry cloning
- Entry listing and reporting
- Entry deletion

Key features:
- Boot entry definition
- Integration with boot loaders
- Snapshot support
- Version tracking
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sts.boom.base import BoomBase, BoomConfig, BoomOptions

if TYPE_CHECKING:
    from sts.utils.cmdline import CommandResult


@dataclass
class BoomEntry(BoomBase):
    """Boom boot entry representation.

    Manages boot entries with:
    - Boot loader integration
    - Kernel and initramfs paths
    - Root device configuration
    - Optional mount points

    Args:
        boot_id: Boot identifier (optional, discovered from system)
        title: Entry title (optional, discovered from system)
        version: Kernel version (optional, discovered from system)
        profile_id: OS profile identifier (optional, discovered from system)
        linux: Kernel path (optional, discovered from system)
        initramfs: Initramfs path (optional, discovered from system)
        root_device: Root device path (optional, discovered from system)
        root_lv: Root logical volume (optional, discovered from system)
        options: Additional kernel options (optional, discovered from system)
        machine_id: Machine identifier (optional, discovered from system)
        btrfs_subvol_path: BTRFS subvolume path (optional, discovered from system)
        btrfs_subvol_id: BTRFS subvolume ID (optional, discovered from system)
        entry_path: Path to entry configuration file (optional, discovered from system)
        entry_file: Entry configuration filename (optional, discovered from system)
        readonly: Whether the entry is read-only (optional, discovered from system)

    Example:
        ```python
        entry = BoomEntry()  # Discovers first available entry
        entry = BoomEntry(boot_id='abc123')  # Discovers specific entry
        ```
    """

    COMMAND: str = 'entry'

    boot_id: str | None = None
    title: str | None = None
    version: str | None = None
    profile_id: str | None = None
    linux: str | None = None
    initramfs: str | None = None
    root_device: str | None = None
    root_lv: str | None = None
    options: str | None = None
    machine_id: str | None = None
    btrfs_subvol_path: str | None = None
    btrfs_subvol_id: int | None = None
    entry_path: str | None = None
    entry_file: str | None = None
    readonly: bool = False

    def __post_init__(self) -> None:
        """Initialize boot entry.

        Discovery process:
        1. Initialize base class
        2. Find entry info if boot_id provided
        3. Set entry attributes
        """
        # Initialize base class with default config
        super().__init__(config=BoomConfig())

        # Discover entry info if boot_id provided
        if self.boot_id:
            self._load_entry_data()

    def _load_entry_data(self) -> bool:
        """Load entry data from system.

        Uses 'boom entry list' to get entry details.
        Updates instance attributes with loaded data.
        """
        if not self.boot_id:
            return False

        options = {'--boot-id': self.boot_id, '--options': '+entry_all,param_all,profile_all', '--json': None}

        result = self.run_command(command=self.COMMAND, subcommand='list', options=options)

        if not result.succeeded or not result.stdout:
            logging.warning(f'Failed to load entry data for boot_id: {self.boot_id}')
            return False

        try:
            data = json.loads(result.stdout)
            if not data or 'Entries' not in data or not data['Entries']:
                return False

            entry_data = data['Entries'][0]
            self.title = entry_data.get('entry_title')
            self.version = entry_data.get('param_version')
            self.profile_id = entry_data.get('profile_osid')
            self.linux = entry_data.get('entry_kernel')
            self.initramfs = entry_data.get('entry_initramfs')
            self.root_device = entry_data.get('param_rootdev')
            self.root_lv = entry_data.get('param_rootlv')
            self.options = entry_data.get('entry_options')
            self.machine_id = entry_data.get('entry_machineid')
            self.btrfs_subvol_path = entry_data.get('param_subvolpath')
            self.btrfs_subvol_id = entry_data.get('param_subvolid')
            self.entry_path = entry_data.get('entry_entrypath')
            self.entry_file = entry_data.get('entry_entryfile')
            self.readonly = entry_data.get('entry_readonly', False)

        except (json.JSONDecodeError, AttributeError) as e:
            logging.warning(f'Error parsing entry data: {e}')
            return False
        return True

    def refresh_info(self) -> bool:
        """Refresh entry information.

        Retrieves detailed information about the entry:
        - Updates entry attributes
        - Gets latest status and configuration
        - Ensures data is current

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            entry = BoomEntry(boot_id='abc123')
            entry.refresh_info()  # Update with latest information
            ```
        """
        if not self._load_entry_data():
            logging.warning('No identifiers available for entry refresh')
            return False
        return True

    @staticmethod
    def _set_kernel_options(
        *,
        options: BoomOptions,
        version: str | None = None,
        linux: str | None = None,
        initramfs: str | None = None,
    ) -> None:
        """Sets kernel-related options in the provided dictionary.

        This helper method was created to comply with Ruff's complexity warning.
        """
        if version:
            options['--version'] = version
        if linux:
            options['--linux'] = linux
        if initramfs:
            options['--initrd'] = initramfs

    @staticmethod
    def _set_boot_options(
        *,
        options: BoomOptions,
        add_opts: str | None = None,
        del_opts: str | None = None,
        backup: bool = False,
        update: bool = False,
        no_fstab: bool = False,
        mount: str | None = None,
        swap: str | None = None,
    ) -> None:
        """Sets general boot options in the provided dictionary.

        This helper method was created to comply with Ruff's complexity warning.
        """
        if add_opts:
            options['--add-opts'] = add_opts
        if del_opts:
            options['--del-opts'] = del_opts
        if backup:
            options['--backup'] = None
        if update:
            options['--update'] = None
        if no_fstab:
            options['--no-fstab'] = None
        if mount:
            options['--mount'] = mount
        if swap:
            options['--swap'] = swap

    @staticmethod
    def _set_device_options(
        *,
        options: BoomOptions,
        root_device: str | None = None,
        root_lv: str | None = None,
    ) -> None:
        """Sets device-related options in the provided dictionary.

        This helper method was created to comply with Ruff's complexity warning.
        """
        if root_device:
            options['--root-device'] = root_device
        if root_lv:
            options['--root-lv'] = root_lv

    def create(
        self,
        *,
        title: str | None = None,
        version: str | None = None,
        profile_id: str | None = None,
        root_device: str | None = None,
        root_lv: str | None = None,
        linux: str | None = None,
        initramfs: str | None = None,
        btrfs_subvol: str | None = None,
        add_opts: str | None = None,
        del_opts: str | None = None,
        mount: str | None = None,
        swap: str | None = None,
        backup: bool = False,
        update: bool = False,
        no_fstab: bool = False,
    ) -> bool:
        """Create boot entry.

        Creates entry with:
        - Required boot parameters
        - Optional configuration
        - Optional image backup
        - Optional mount points

        Args:
            title: Entry title
            version: Kernel version
            profile_id: OS profile identifier
            root_device: Root device path
            root_lv: Root logical volume
            linux: Kernel path
            initramfs: Initramfs path
            btrfs_subvol: BTRFS subvolume path or ID
            add_opts: Additional kernel options
            del_opts: Options to remove from defaults
            backup: Backup boot images
            update: Update existing backups
            no_fstab: Disable /etc/fstab processing
            mount: Mount configuration (format: what:where:fstype:options)
            swap: Swap configuration (format: what:options)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            entry.create(title='System Snapshot', root_lv='vg00/lvol0-snap', backup=True)
            True
            ```
        """
        options: BoomOptions = {}

        # Set required title
        if not title and not self.title:
            logging.error('Title is required for creating a boot entry')
            return False

        options['--title'] = title or self.title
        if profile_id or self.profile_id:
            options['--profile'] = profile_id or self.profile_id

        self._set_kernel_options(options=options, version=version, linux=linux, initramfs=initramfs)
        self._set_device_options(options=options, root_device=root_device, root_lv=root_lv)
        self._set_boot_options(
            options=options,
            add_opts=add_opts,
            del_opts=del_opts,
            backup=backup,
            update=update,
            no_fstab=no_fstab,
            mount=mount,
            swap=swap,
        )

        # Handle BTRFS subvolume
        subvol_to_use = None
        if btrfs_subvol:
            subvol_to_use = btrfs_subvol
        elif self.btrfs_subvol_path:
            subvol_to_use = self.btrfs_subvol_path
        elif self.btrfs_subvol_id is not None and self.btrfs_subvol_id >= 0:
            subvol_to_use = str(self.btrfs_subvol_id)

        if subvol_to_use:
            options['--btrfs-subvol'] = subvol_to_use

        result = self.run_command(
            command=self.COMMAND,
            subcommand='create',
            options=options,
        )

        if not result.succeeded:
            return False

        # Extract new boot_id from output
        for line in result.stdout.splitlines():
            m = re.search(r'boot_id\s+(\w+)', line)
            if m:
                self.boot_id = m.group(1)
                return self._load_entry_data()
        logging.warning('Could not parse boot_id from create output')
        return False

    def delete(self) -> bool:
        """Delete boot entry.

        Removes entry:
        - Removes from boot loader
        - Does not affect boot images
        - Cannot be undone

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            entry.delete()
            True
            ```
        """
        if not self.boot_id:
            logging.error('Boot ID required for deletion')
            return False

        options: BoomOptions = {'--boot-id': self.boot_id}

        result = self.run_command(command=self.COMMAND, subcommand='delete', options=options)

        return result.succeeded

    def clone(
        self,
        *,
        title: str | None = None,
        version: str | None = None,
        profile_id: str | None = None,
        root_device: str | None = None,
        root_lv: str | None = None,
        linux: str | None = None,
        initramfs: str | None = None,
        btrfs_subvol: str | None = None,
        add_opts: str | None = None,
        del_opts: str | None = None,
        mount: str | None = None,
        swap: str | None = None,
        backup: bool = False,
        update: bool = False,
        no_fstab: bool = False,
    ) -> BoomEntry | None:
        """Clone boot entry.

        Creates a new entry based on this one:
        - Maintains consistent configuration
        - Applies specified changes
        - Optionally backs up images
        - Creates new boot_id

        Args:
            title: Entry title
            version: Kernel version
            profile_id: OS profile identifier
            root_device: Root device path
            root_lv: Root logical volume
            linux: Kernel path
            initramfs: Initramfs path
            btrfs_subvol: BTRFS subvolume path or ID
            add_opts: Additional kernel options
            del_opts: Options to remove from defaults
            backup: Backup boot images
            update: Update existing backups
            no_fstab: Disable /etc/fstab processing
            mount: Mount configuration (format: what:where:fstype:options)
            swap: Swap configuration (format: what:options)

        Returns:
            New BoomEntry instance or None if failed

        Example:
            ```python
            new_entry = entry.clone(title='System Snapshot 2', root_lv='vg00/lvol0-snap2')
            ```
        """
        if not self.boot_id:
            logging.error('Original boot entry ID required for cloning')
            return None

        options: BoomOptions = {
            '--boot-id': self.boot_id,
        }

        if title:
            options['--title'] = title
        if profile_id:
            options['--profile'] = profile_id
        if btrfs_subvol:
            options['--btrfs-subvol'] = btrfs_subvol

        self._set_kernel_options(options=options, version=version, linux=linux, initramfs=initramfs)
        self._set_device_options(options=options, root_device=root_device, root_lv=root_lv)
        self._set_boot_options(
            options=options,
            add_opts=add_opts,
            del_opts=del_opts,
            backup=backup,
            update=update,
            no_fstab=no_fstab,
            mount=mount,
            swap=swap,
        )

        result = self.run_command(
            command=self.COMMAND,
            subcommand='clone',
            options=options,
        )

        if not result.succeeded:
            return None

        # Extract new boot_id from output
        for line in result.stdout.splitlines():
            # Parse output like "Created entry with boot_id abc123:"
            m = re.search(r'boot_id\s+\w+\s+as\s+boot_id\s+(\w+)', line)
            if m:
                # Only the first 7 characters of os_id_full are used as ID
                return BoomEntry(boot_id=m.group(1))
        logging.warning('Could not parse boot_id from clone output')
        return None

    def show(self) -> CommandResult:
        """Show boot entry configuration.

        Displays detailed information:
        - Boot loader entry format
        - All entry parameters
        - Associated profile information

        Returns:
            Command result

        Example:
            ```python
            result = entry.show()
            print(result.stdout)
            ```
        """
        options: BoomOptions = {}
        if self.boot_id:
            options = {'--boot-id': self.boot_id}

        return self.run_command(command=self.COMMAND, subcommand='show', options=options)

    def list(
        self,
        boot_id: str | None = None,
        profile_id: str | None = None,
        version: str | None = None,
        title: str | None = None,
        root_device: str | None = None,
        root_lv: str | None = None,
        options: BoomOptions | None = None,
    ) -> CommandResult:
        """List boot entries.

        Lists entries matching criteria:
        - Filtered by parameters
        - Returns the raw CommandResult from the Boom CLI

        Args:
            boot_id: Filter by boot ID
            profile_id: Filter by OS profile ID
            version: Filter by kernel version
            title: Filter by entry title
            root_device: Filter by root device
            root_lv: Filter by root LV
            options: Custom output format

        Returns:
           Command result with list output

        Example:
            ```python
            result = entry.title(name='Fedora')
            print(result.stdout)
            ```
        """
        # Build filter options
        if not options:
            options = {}

        if boot_id:
            options['--boot-id'] = boot_id
        if profile_id:
            options['--profile'] = profile_id
        if version:
            options['--version'] = version
        if title:
            options['--title'] = title
        if root_device:
            options['--root-device'] = root_device
        if root_lv:
            options['--root-lv'] = root_lv

        return self.run_command(command=self.COMMAND, subcommand='list', options=options)

    @classmethod
    def get_all(cls) -> list[BoomEntry]:
        """Get all boot entries.

        Retrieves information about all boot entries:
        - Lists all entries in system
        - Creates instances with attributes
        - Filters by optional criteria

        Args:
            version: Filter by kernel version
            title: Filter by entry title
            root_device: Filter by root device path
            root_lv: Filter by root logical volume
            profile_id: Filter by OS profile ID
            include_readonly: Whether to include read-only entries

        Returns:
            List of BoomEntry instances

        Example:
            ```python
            # Get all boot entries
            entries = BoomEntry.get_all()
            ```
        """
        entries = []
        options: BoomOptions = {'--options': '+entry_all,param_all,profile_all', '--json': None}

        base = cls()

        # Use the list method to get host profiles
        result = base.run_command(command=base.COMMAND, subcommand='list', options=options)
        if not result.succeeded:
            logging.warning(f'Could not get list of entries: {result.stderr}')
            return entries
        try:
            data = json.loads(result.stdout)
            if not data or 'Entries' not in data or not data['Entries']:
                return entries

            entries_data = data['Entries']

            for entry_data in entries_data:
                if 'entry_bootid' not in entry_data:
                    continue

                # Only the first 7 characters of id full are used as ID
                entry = cls(
                    boot_id=entry_data.get('entry_bootid')[:7],
                    title=entry_data.get('entry_title'),
                    version=entry_data.get('param_version'),
                    profile_id=entry_data.get('profile_osid'),
                    linux=entry_data.get('entry_kernel'),
                    initramfs=entry_data.get('entry_initramfs'),
                    root_device=entry_data.get('param_rootdev'),
                    root_lv=entry_data.get('param_rootlv'),
                    options=entry_data.get('entry_options'),
                    machine_id=entry_data.get('entry_machineid'),
                    btrfs_subvol_path=entry_data.get('param_subvolpath'),
                    btrfs_subvol_id=entry_data.get('param_subvolid'),
                    entry_path=entry_data.get('entry_entrypath'),
                    entry_file=entry_data.get('entry_entryfile'),
                    readonly=entry_data.get('entry_readonly', False),
                )

                entries.append(entry)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.warning(f'Error parsing entry list data: {e}')

        return entries
