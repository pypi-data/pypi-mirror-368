# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Boom OS profile management.

This module provides functionality for managing Boom OS profiles:
- Profile creation and management
- Profile template configuration
- Profile discovery and matching
- Profile reporting

Key features:
- OS identification
- Boot option templates
- Kernel version patterns
- Image path management
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
class BoomProfile(BoomBase):
    """Boom OS profile representation.

    Manages OS profiles with:
    - OS identity information
    - Template patterns
    - Boot option configuration

    Args:
        os_id: OS identifier (optional, discovered from system)
        name: OS name (optional, discovered from system)
        short_name: OS short name (optional, discovered from system)
        version: OS version (optional, discovered from system)
        version_id: OS version ID (optional, discovered from system)
        uname_pattern: UTS release pattern (optional, discovered from system)
        kernel_pattern: Kernel path pattern (optional, discovered from system)
        initrd_pattern: Initramfs path pattern (optional, discovered from system)
        lvm_opts: LVM2 root options template (optional, discovered from system)
        btrfs_opts: BTRFS root options template (optional, discovered from system)
        options: Kernel options template (optional, discovered from system)
        profile_path: Path to profile configuration file (optional, discovered from system)
        report: Profile report (optional, discovered from system)

    Example:
        ```python
        profile = BoomProfile()  # Discovers first available profile
        profile = BoomProfile(os_id='abc123')  # Discovers specific profile
        ```
    """

    COMMAND: str = 'profile'

    os_id: str | None = None
    name: str | None = None
    short_name: str | None = None
    version: str | None = None
    version_id: str | None = None
    uname_pattern: str | None = None
    kernel_pattern: str | None = None
    initrd_pattern: str | None = None
    lvm_opts: str | None = None
    btrfs_opts: str | None = None
    options: str | None = None
    profile_path: str | None = None

    def __post_init__(self) -> None:
        """Initialize OS profile.

        Discovery process:
        1. Initialize base class
        2. Find profile info if os_id provided
        3. Set profile attributes
        """
        # Initialize base class with default config
        super().__init__(config=BoomConfig())

        # Discover profile info if os_id provided
        if self.os_id:
            self._load_profile_data()

    def _load_profile_data(self) -> bool:
        """Load profile data from system.

        Uses 'boom profile list' to get profile details.
        Updates instance attributes with loaded data.
        """
        if not self.os_id:
            return False

        options = {'--profile': self.os_id, '--options': '+profile_all', '--json': None}

        result = self.run_command(command=self.COMMAND, subcommand='list', options=options)

        if not result.succeeded or not result.stdout:
            logging.warning(f'Failed to load profile data for os_id: {self.os_id}')
            return False

        try:
            data = json.loads(result.stdout)
            if not data or 'OsProfiles' not in data or not data['OsProfiles']:
                return False

            profile_data = data['OsProfiles'][0]
            self.name = profile_data.get('profile_osname')
            self.short_name = profile_data.get('profile_osshortname')
            self.version = profile_data.get('profile_osversion')
            self.version_id = profile_data.get('profile_osversion_id')
            self.uname_pattern = profile_data.get('profile_unamepattern')
            self.kernel_pattern = profile_data.get('profile_kernelpattern')
            self.initrd_pattern = profile_data.get('profile_initrdpattern')
            self.lvm_opts = profile_data.get('profile_lvm2opts')
            self.btrfs_opts = profile_data.get('profile_btrfsopts')
            self.options = profile_data.get('profile_options')
            self.profile_path = profile_data.get('profile_profilepath')

        except (json.JSONDecodeError, AttributeError) as e:
            logging.warning(f'Error parsing profile data: {e}')
            return False

        return True

    def refresh_info(self) -> bool:
        """Refresh profile information.

        Retrieves detailed information about the profile:
        - Updates profile attributes
        - Gets latest configuration
        - Ensures data is current

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            profile = BoomProfile(os_id='abc123')
            profile.refresh_info()  # Update with latest information
            ```
        """
        if self._load_profile_data():
            return True
        logging.warning('There was a problem loading profile data!')
        return False

    @staticmethod
    def _set_options(
        *,
        options_dict: BoomOptions,
        version: str | None = None,
        version_id: str | None = None,
        uname_pattern: str | None = None,
        kernel_pattern: str | None = None,
        initrd_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        from_host: bool = False,
        os_release: str | None = None,
    ) -> None:
        """Helper function to set command options."""
        if version:
            options_dict['--os-version'] = version
        if version_id:
            options_dict['--os-version-id'] = version_id
        if uname_pattern:
            options_dict['--uname-pattern'] = uname_pattern
        if kernel_pattern:
            options_dict['--kernel-pattern'] = kernel_pattern
        if initrd_pattern:
            options_dict['--initramfs-pattern'] = initrd_pattern
        if lvm_opts:
            options_dict['--lvm-opts'] = lvm_opts
        if btrfs_opts:
            options_dict['--btrfs-opts'] = btrfs_opts
        if from_host:
            options_dict['--from-host'] = None
        if os_release:
            options_dict['--os-release'] = os_release

    def create(
        self,
        *,
        name: str | None = None,
        short_name: str | None = None,
        version: str | None = None,
        version_id: str | None = None,
        uname_pattern: str | None = None,
        from_host: bool = False,
        os_release: str | None = None,
        kernel_pattern: str | None = None,
        initrd_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        options: str | None = None,
    ) -> bool:
        """Create OS profile.

        Creates profile with:
        - Required OS identity information
        - Template patterns
        - Optional configuration

        Args:
            name: OS name
            short_name: OS short name
            version: OS version
            version_id: OS version ID
            uname_pattern: UTS release pattern (required if not from_host)
            from_host: Use current host's OS information
            os_release: Path to os-release file
            kernel_pattern: Kernel path pattern
            initrd_pattern: Initramfs path pattern
            lvm_opts: LVM2 root options template
            btrfs_opts: BTRFS root options template
            options: Kernel options template

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            profile.create(
                name='Fedora',
                short_name='fedora',
                version='36',
                version_id='36',
                uname_pattern='fc36',
            )
            True
            ```
        """
        options_dict: BoomOptions = {}

        # Set parameters
        if name:
            options_dict['--name'] = name
        if short_name:
            options_dict['--short-name'] = short_name
        if options:
            options_dict['--os-options'] = options

        self._set_options(
            options_dict=options_dict,
            version=version,
            version_id=version_id,
            uname_pattern=uname_pattern,
            from_host=from_host,
            os_release=os_release,
            kernel_pattern=kernel_pattern,
            initrd_pattern=initrd_pattern,
            lvm_opts=lvm_opts,
            btrfs_opts=btrfs_opts,
        )

        result = self.run_command(
            command=self.COMMAND,
            subcommand='create',
            options=options_dict,
        )

        if not result.succeeded:
            return False

        # Extract os_id from output
        for line in result.stdout.splitlines():
            if match := re.match(r'\s*OS ID:\s*"([^"]+)"', line):
                # Only the first 7 characters of os_id_full are used as ID
                self.os_id = match.group(1)[:7]
                if not self._load_profile_data():
                    logging.warning('Could not parse os_id from create output')
                    return False
                return True

        logging.warning('Could not parse os_id from create output')
        return False

    def delete(self) -> bool:
        """Delete OS profile.

        Removes profile:
        - Does not affect boot entries
        - Cannot be undone

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            profile.delete()
            True
            ```
        """
        if not self.os_id:
            logging.error('OS ID required for deletion')
            return False

        options: BoomOptions = {'--profile': self.os_id}

        result = self.run_command(command=self.COMMAND, subcommand='delete', options=options)

        return result.succeeded

    def clone(
        self,
        name: str | None = None,
        short_name: str | None = None,
        version: str | None = None,
        version_id: str | None = None,
        uname_pattern: str | None = None,
        kernel_pattern: str | None = None,
        initrd_pattern: str | None = None,
        lvm_opts: str | None = None,
        btrfs_opts: str | None = None,
        options: str | None = None,
    ) -> BoomProfile | None:
        """Clone OS profile.

        Creates a new profile based on this one:
        - Maintains consistent configuration
        - Applies specified changes
        - Creates new os_id

        Args:
            name: OS name
            short_name: OS short name
            version: OS version
            version_id: OS version ID
            uname_pattern: UTS release pattern
            kernel_pattern: Kernel path pattern
            initrd_pattern: Initramfs path pattern
            lvm_opts: LVM2 root options template
            btrfs_opts: BTRFS root options template
            options: Kernel options template

        Returns:
            New BoomProfile instance or None if failed

        Example:
            ```python
            new_profile = profile.clone(version='37', version_id='37', uname_pattern='fc37')
            ```
        """
        if not self.os_id:
            logging.error('Original OS profile ID required for cloning')
            return None

        options_dict: BoomOptions = {
            '--profile': self.os_id,
        }

        # Set optional parameters
        if name:
            options_dict['--name'] = name
        if short_name:
            options_dict['--short-name'] = short_name
        if options:
            options_dict['--os-options'] = options

        self._set_options(
            options_dict=options_dict,
            version=version,
            version_id=version_id,
            uname_pattern=uname_pattern,
            kernel_pattern=kernel_pattern,
            initrd_pattern=initrd_pattern,
            lvm_opts=lvm_opts,
            btrfs_opts=btrfs_opts,
        )

        result = self.run_command(
            command=self.COMMAND,
            subcommand='clone',
            options=options_dict,
        )

        if not result.succeeded:
            return None
        # Extract new os_id from output
        for line in result.stdout.splitlines():
            if match := re.match(r'\s*OS ID:\s*"([^"]+)"', line):
                # Only the first 7 characters of os_id_full are used as ID
                return BoomProfile(os_id=match.group(1)[:7])

        logging.warning('Could not parse os_id from clone output')
        return None

    def show(self) -> CommandResult:
        """Show OS profile configuration.

        Displays detailed information:
        - Profile identity information
        - Template patterns
        - Configuration options

        Returns:
            Command result

        Example:
            ```python
            result = profile.show()
            print(result.stdout)
            ```
        """
        options: BoomOptions = {}
        if self.os_id:
            options = {'--profile': self.os_id}

        return self.run_command(command=self.COMMAND, subcommand='show', options=options)

    def list(
        self,
        os_id: str | None = None,
        name: str | None = None,
        short_name: str | None = None,
        version: str | None = None,
        version_id: str | None = None,
        options: BoomOptions | None = None,
    ) -> CommandResult:
        """List OS profiles.

        Lists profiles matching criteria:
        - Filtered by parameters
        - Returns command result with list output
        - Customizable output format

        Args:
            os_id: Filter by OS ID
            name: Filter by OS name
            short_name: Filter by OS short name
            version: Filter by OS version
            version_id: Filter by OS version ID
            options: Additional options for the command

        Returns:
            Command result with list output

        Example:
            ```python
            result = profile.list(name='Fedora')
            print(result.stdout)
            ```
        """
        # Build filter options
        if not options:
            options = {}

        if os_id:
            options['--profile'] = os_id
        if name:
            options['--name'] = name
        if short_name:
            options['--short-name'] = short_name
        if version:
            options['--os-version'] = version
        if version_id:
            options['--os-version-id'] = version_id

        return self.run_command(command=self.COMMAND, subcommand='list', options=options)

    @classmethod
    def get_all(cls) -> list[BoomProfile]:
        """Get all OS profiles.

        Retrieves information about all OS profiles:
        - Lists all profiles in system
        - Creates instances with attributes

        Returns:
            List of BoomProfile instances

        Example:
            ```python
            # Get all OS profiles
            profiles = BoomProfile.get_all()
            ```
        """
        profiles = []
        options: BoomOptions = {'--options': '+profile_all', '--json': None}

        base = cls()

        # Use the list method to get profiles
        result = base.run_command(command=base.COMMAND, subcommand='list', options=options)

        if not result.succeeded or not result.stdout:
            return profiles

        try:
            data = json.loads(result.stdout)
            if not data or 'OsProfiles' not in data or not data['OsProfiles']:
                return profiles

            profiles_data = data['OsProfiles']

            for profile_data in profiles_data:
                if 'profile_osid' not in profile_data:
                    continue

                # Only the first 7 characters of id full are used as ID
                profile = cls(
                    os_id=profile_data.get('profile_osid')[:7],
                    name=profile_data.get('profile_osname'),
                    short_name=profile_data.get('profile_osshortname'),
                    version=profile_data.get('profile_osversion'),
                    version_id=profile_data.get('profile_osversion_id'),
                    uname_pattern=profile_data.get('profile_unamepattern'),
                    kernel_pattern=profile_data.get('profile_kernelpattern'),
                    initrd_pattern=profile_data.get('profile_initrdpattern'),
                    lvm_opts=profile_data.get('profile_lvm2opts'),
                    btrfs_opts=profile_data.get('profile_btrfsopts'),
                    options=profile_data.get('profile_options'),
                    profile_path=profile_data.get('profile_profilepath'),
                )

                profiles.append(profile)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.warning(f'Error parsing profile list data: {e}')

        return profiles
