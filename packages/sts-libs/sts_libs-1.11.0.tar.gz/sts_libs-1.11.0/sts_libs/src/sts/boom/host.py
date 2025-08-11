# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Boom host profile management.

This module provides functionality for managing Boom host profiles:
- Host profile creation and management
- Host-specific template configuration
- Machine-specific customization
- Host boot options

Key features:
- Machine identification
- Per-host configuration
- Boot option customization
- OS profile integration
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
class BoomHost(BoomBase):
    """Boom host profile representation.

    Manages host profiles with:
    - Host identity information
    - Machine-specific configuration
    - Template pattern overrides

    Args:
        host_id: Host identifier (optional, discovered from system)
        name: Host name (optional, discovered from system)
        short_name: Host short name (optional, discovered from system)
        profile_id: OS profile identifier (optional, discovered from system)
        machine_id: Machine identifier (optional, discovered from system)
        kernel_pattern: Kernel path pattern (optional, discovered from system)
        initramfs_pattern: Initramfs path pattern (optional, discovered from system)
        lvm_opts: LVM2 root options template (optional, discovered from system)
        btrfs_opts: BTRFS root options template (optional, discovered from system)
        options: Kernel options template (optional, discovered from system)
        host_profile_path: Path to host profile configuration file (optional, discovered from system)
        report: Host report (optional, discovered from system)

    Example:
        ```python
        host = BoomHost()  # Discovers first available host profile
        host = BoomHost(host_id='abc123')  # Discovers specific host profile
        ```
    """

    COMMAND: str = 'host'

    host_id: str | None = None
    name: str | None = None
    short_name: str | None = None
    profile_id: str | None = None
    machine_id: str | None = None
    kernel_pattern: str | None = None
    initramfs_pattern: str | None = None
    lvm_opts: str | None = None
    btrfs_opts: str | None = None
    options: str | None = None
    host_profile_path: str | None = None
    host_label: str | None = None

    def __post_init__(self) -> None:
        """Initialize host profile.

        Discovery process:
        1. Initialize base class
        2. Find host profile info if host_id provided
        3. Set host attributes
        """
        # Initialize base class with default config
        super().__init__(config=BoomConfig())

        # Discover host profile info if host_id provided
        if self.host_id:
            self._load_host_data()

    def _load_host_data(self) -> bool:
        """Load host profile data from system.

        Uses 'boom host list' to get host profile details.
        Updates instance attributes with loaded data.
        """
        if not self.host_id:
            return False

        options = {'--host-profile': self.host_id, '--options': '+host_all', '--json': None}

        result = self.run_command(command=self.COMMAND, subcommand='list', options=options)

        if not result.succeeded or not result.stdout:
            logging.warning(f'Failed to load host profile data for host_id: {self.host_id}')
            return False

        try:
            data = json.loads(result.stdout)
            if not data or 'HostProfiles' not in data or not data['HostProfiles']:
                return False

            host_data = data['HostProfiles'][0]
            self.name = host_data.get('host_hostname')
            self.profile_id = host_data.get('host_osid')
            self.machine_id = host_data.get('host_machineid')
            self.kernel_pattern = host_data.get('host_kernelpattern')
            self.initramfs_pattern = host_data.get('host_initrdpattern')
            self.lvm_opts = host_data.get('host_lvm2opts')
            self.btrfs_opts = host_data.get('host_btrfsopts')
            self.options = host_data.get('host_options')
            self.host_profile_path = host_data.get('host_hostprofilepath')
            self.host_label = host_data.get('host_label')

        except (json.JSONDecodeError, AttributeError) as e:
            logging.warning(f'Error parsing host profile data: {e}')
            return False

        return True

    def refresh_info(self) -> bool:
        """Refresh host profile information.

        Retrieves detailed information about the host profile:
        - Updates host profile attributes
        - Gets latest configuration
        - Ensures data is current

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            host = BoomHost(host_id='abc123')
            host.refresh_info()  # Update with latest information
            ```
        """
        if self._load_host_data():
            return True
        logging.warning('No identifiers available for host profile refresh')
        return False

    @staticmethod
    def _set_options(
        options_dict: BoomOptions,
        profile_id: str | None = None,
        machine_id: str | None = None,
        kernel_pattern: str | None = None,
        initramfs_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        options: str | None = None,
        label: str | None = None,
    ) -> None:
        """Helper function to set command options."""
        if profile_id:
            options_dict['--profile'] = profile_id
        if machine_id:
            options_dict['--machine-id'] = machine_id
        if kernel_pattern:
            options_dict['--kernel-pattern'] = kernel_pattern
        if initramfs_pattern:
            options_dict['--initramfs-pattern'] = initramfs_pattern
        if lvm_opts:
            options_dict['--lvm-opts'] = lvm_opts
        if btrfs_opts:
            options_dict['--btrfs-opts'] = btrfs_opts
        if options:
            options_dict['--os-options'] = options
        if label:
            options_dict['--label'] = label

    def create(
        self,
        name: str | None = None,
        short_name: str | None = None,
        profile_id: str | None = None,
        machine_id: str | None = None,
        kernel_pattern: str | None = None,
        initramfs_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        options: str | None = None,
    ) -> bool:
        """Create host profile.

        Creates host profile with:
        - Host identification
        - Machine-specific configuration
        - OS profile integration

        Args:
            name: Host name
            short_name: Host short name
            profile_id: OS profile identifier (required)
            machine_id: Machine identifier (required)
            kernel_pattern: Kernel pattern override
            initramfs_pattern: Initramfs pattern override
            lvm_opts: LVM options override
            btrfs_opts: BTRFS options override
            options: Kernel options override

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            host.create(name='webserver', profile_id='3fc389b', machine_id='611f38fd887d41dea7eb3403b2730a76')
            True
            ```
        """
        options_dict: BoomOptions = {}

        # Set parameters
        if name or self.name:
            options_dict['--name'] = name or self.name
        if short_name or self.short_name:
            options_dict['--short-name'] = short_name or self.short_name

        self._set_options(
            options_dict,
            profile_id=profile_id or self.profile_id,
            machine_id=machine_id or self.machine_id,
            kernel_pattern=kernel_pattern or self.kernel_pattern,
            initramfs_pattern=initramfs_pattern or self.initramfs_pattern,
            lvm_opts=lvm_opts or self.lvm_opts,
            btrfs_opts=btrfs_opts or self.btrfs_opts,
            options=options or self.options,
        )

        result = self.run_command(
            command=self.COMMAND,
            subcommand='create',
            options=options_dict,
        )

        if not result.succeeded:
            return False
        # Extract host_id from output
        for line in result.stdout.splitlines():
            if match := re.match(r'\s*Host ID:\s*"([^"]+)"', line):
                # Only the first 7 characters of full host id are used as ID
                self.host_id = match.group(1)[:7]
                if not self._load_host_data():
                    logging.warning('Could not parse os_id from create output')
                    return False
                return True
        return False

    def delete(self) -> bool:
        """Delete host profile.

        Removes host profile:
        - Does not affect OS profiles or boot entries
        - Cannot be undone

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            host.delete()
            True
            ```
        """
        if not self.host_id:
            logging.error('Host ID required for deletion')
            return False

        options: BoomOptions = {'--host-profile': self.host_id}

        result = self.run_command(command=self.COMMAND, subcommand='delete', options=options)

        return result.succeeded

    def clone(
        self,
        name: str | None = None,
        short_name: str | None = None,
        profile_id: str | None = None,
        machine_id: str | None = None,
        kernel_pattern: str | None = None,
        initramfs_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        options: str | None = None,
        label: str | None = None,
    ) -> BoomHost | None:
        """Clone host profile.

        Creates a new host profile based on this one:
        - Maintains consistent configuration
        - Applies specified changes
        - Creates new host_id

        Args:
            name: Host name
            short_name: Host short name
            profile_id: OS profile identifier
            machine_id: Machine identifier
            kernel_pattern: Kernel pattern override
            initramfs_pattern: Initramfs pattern override
            lvm_opts: LVM options override
            btrfs_opts: BTRFS options override
            options: Kernel options override
            label: Description if host profile
        Returns:
            New BoomHost instance or None if failed

        Example:
            ```python
            new_host = host.clone(name='webserver2', machine_id='722f38fd887d41dea7eb3403b2730a77')
            ```
        """
        if not self.host_id:
            logging.error('Original host profile ID required for cloning')
            return None

        options_dict: BoomOptions = {
            '--host-profile': self.host_id,
        }

        # Set optional parameters
        if name:
            options_dict['--name'] = name
        if short_name:
            options_dict['--short-name'] = short_name

        self._set_options(
            options_dict,
            profile_id=profile_id,
            machine_id=machine_id,
            kernel_pattern=kernel_pattern,
            initramfs_pattern=initramfs_pattern,
            lvm_opts=lvm_opts,
            btrfs_opts=btrfs_opts,
            options=options,
            label=label,
        )

        result = self.run_command(
            command=self.COMMAND,
            subcommand='clone',
            options=options_dict,
        )

        if not result.succeeded:
            return None
        # Extract new host_id from output
        for line in result.stdout.splitlines():
            if match := re.match(r'\s*Host ID:\s*"([^"]+)"', line):
                # Only the first 7 characters of os_id_full are used as ID
                return BoomHost(host_id=match.group(1)[:7])
        return None

    def edit(
        self,
        name: str | None = None,
        short_name: str | None = None,
        profile_id: str | None = None,
        machine_id: str | None = None,
        kernel_pattern: str | None = None,
        initramfs_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        options: str | None = None,
    ) -> bool:
        """Edit host profile.

        Modifies existing host profile:
        - Updates specified fields
        - Preserves host_id
        - Maintains other settings

        Args:
            name: Host name
            short_name: Host short name
            profile_id: OS profile identifier
            machine_id: Machine identifier
            kernel_pattern: Kernel pattern override
            initramfs_pattern: Initramfs pattern override
            lvm_opts: LVM options override
            btrfs_opts: BTRFS options override
            options: Kernel options override

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            host.edit(name='webserver-updated', options='root=/dev/vg00/lvol0 ro quiet')
            True
            ```
        """
        if not self.host_id:
            logging.error('Host ID required for edit operation')
            return False

        options_dict: BoomOptions = {
            '--host-profile': self.host_id,
        }

        # Set optional parameters
        if name:
            options_dict['--name'] = name
        if short_name:
            options_dict['--short-name'] = short_name

        self._set_options(
            options_dict,
            profile_id=profile_id or self.profile_id,
            machine_id=machine_id or self.machine_id,
            kernel_pattern=kernel_pattern or self.kernel_pattern,
            initramfs_pattern=initramfs_pattern or self.initramfs_pattern,
            lvm_opts=lvm_opts or self.lvm_opts,
            btrfs_opts=btrfs_opts or self.btrfs_opts,
            options=options or self.options,
        )

        result = self.run_command(
            command=self.COMMAND,
            subcommand='edit',
            options=options_dict,
        )

        if not result.succeeded:
            return False

        # Reload host profile data
        self._load_host_data()
        return True

    def show(self) -> CommandResult:
        """Show host profile configuration.

        Displays detailed information:
        - Host profile identity information
        - Template pattern overrides
        - Configuration options

        Returns:
            Command result

        Example:
            ```python
            result = host.show()
            print(result.stdout)
            ```
        """
        options: BoomOptions = {}
        if self.host_id:
            options = {'--host-profile': self.host_id}

        return self.run_command(command=self.COMMAND, subcommand='show', options=options)

    def list(
        self,
        host_id: str | None = None,
        name: str | None = None,
        short_name: str | None = None,
        profile_id: str | None = None,
        machine_id: str | None = None,
        options: BoomOptions | None = None,
    ) -> CommandResult:
        """List host profiles.

        Lists host profiles matching criteria:
        - Filtered by parameters
        - Returns command result with list output
        - Customizable output format

        Args:
            host_id: Filter by host ID
            name: Filter by host name
            short_name: Filter by host short name
            profile_id: Filter by OS profile ID
            machine_id: Filter by machine ID
            options: Additional options for the command

        Returns:
            Command result with list output

        Example:
            ```python
            result = host.list(profile_id='3fc389b')
            print(result.stdout)
            ```
        """
        # Build filter options
        if not options:
            options = {}

        if host_id:
            options['--host-profile'] = host_id
        if name:
            options['--name'] = name
        if short_name:
            options['--short-name'] = short_name
        if profile_id:
            options['--profile'] = profile_id
        if machine_id:
            options['--machine-id'] = machine_id

        return self.run_command(command=self.COMMAND, subcommand='list', options=options)

    @classmethod
    def get_all(
        cls,
    ) -> list[BoomHost]:
        """Get all host profiles.

        Retrieves information about all host profiles:
        - Lists all host profiles in system
        - Creates instances with attributes

        Returns:
            List of BoomHost instances

        Example:
            ```python
            # Get all host profiles
            hosts = BoomHost.get_all()
            ```
        """
        hosts = []
        options: BoomOptions = {'--options': '+host_all', '--json': None}

        base = cls()

        # Use the list method to get host profiles
        result = base.run_command(command=base.COMMAND, subcommand='list', options=options)

        if not result.succeeded or not result.stdout:
            return hosts

        try:
            data = json.loads(result.stdout)
            if not data or 'HostProfiles' not in data or not data['HostProfiles']:
                return hosts

            hosts_data = data['HostProfiles']

            for host_data in hosts_data:
                if 'host_hostid' not in host_data:
                    continue

                # Only the first 7 characters of id full are used as ID
                host = cls(
                    host_id=host_data.get('host_hostid')[:7],
                    name=host_data.get('host_hostname'),
                    profile_id=host_data.get('host_osid'),
                    machine_id=host_data.get('host_machineid'),
                    kernel_pattern=host_data.get('host_kernelpattern'),
                    initramfs_pattern=host_data.get('host_initrdpattern'),
                    lvm_opts=host_data.get('host_lvm2opts'),
                    btrfs_opts=host_data.get('host_btrfsopts'),
                    options=host_data.get('host_options'),
                    host_profile_path=host_data.get('host_hostprofilepath'),
                    host_label=host_data.get('host_label'),
                )

                hosts.append(host)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.warning(f'Error parsing host list data: {e}')

        return hosts
