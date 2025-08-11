# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base Boom functionality.

This module provides base functionality for Boom operations:
- Command execution
- Common utilities

Boom is a boot manager for Linux systems using boot loaders that support
the BootLoader Specification for boot entry configuration.

Boom provides:
- Boot entry management
- OS profile management
- Host profile management
- Filesystem snapshot integration
- Legacy bootloader support
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Union

from sts.utils.cmdline import CommandResult, run

CLI_NAME = 'boom'

# Type definitions
BoomOptions = dict[str, Union[str, None]]  # Command options
BoomReportData = dict[str, Union[str, list[dict[str, Any]]]]  # Report data


@dataclass
class BoomConfig:
    """Boom configuration.

    Controls Boom behavior:
    - Debug settings: Enable subsystem debugging
    - Boot directory: Path to /boot filesystem
    - Verbosity level: Control output verbosity

    Args:
        debug: List of debug subsystems to enable
        boot_dir: Path to /boot filesystem
        verbose: Verbosity level (0-3)

    Examples:
        Create with default settings:
        boom = BoomConfig()

        Create with debug enabled:
        boom = BoomConfig(debug=["profile", "entry"])
    """

    debug: list[str] | None = None  # Enable debugging for subsystems
    boot_dir: str | None = None  # Path to /boot
    verbose: int = 0  # Verbosity level

    def to_args(self) -> list[str]:
        """Convert configuration to command arguments.

        Generates CLI options based on settings:
        - --debug: Enable subsystem debugging
        - --boot-dir: Specify boot directory path
        - --verbose: Increase verbosity

        Returns:
            List of command arguments

        Example:
            ```python
            Get command line arguments:
            config = BoomConfig(debug=["profile", "entry"])
            args = config.to_args()  # Returns ['--debug', 'profile,entry']
            ```
        """
        args = []
        if self.debug:
            debug_str = ','.join(self.debug)
            args.extend(['--debug', debug_str])
        if self.boot_dir:
            args.extend(['--boot-dir', self.boot_dir])
        if self.verbose > 0:
            args.extend(['--verbose'] * self.verbose)
        return args


class BoomBase:
    """Base class for Boom operations.

    Provides common functionality:
    - Command execution with options
    - Error handling
    - Version information
    - Report generation

    Args:
        config: Boom configuration (optional)

    Examples:
        Create with default configuration:
        boom = BoomBase()

        Create with custom configuration:
        boom = BoomBase(BoomConfig(debug=["profile"]))
    """

    def __init__(self, config: BoomConfig | None = None) -> None:
        """Initialize Boom base.

        Args:
            config: Boom configuration
        """
        self.config = config or BoomConfig()

    def run_command(
        self,
        command: str | None = None,
        subcommand: str | None = None,
        action: str | None = None,
        options: BoomOptions | None = None,
        positional_args: list[str] | None = None,
    ) -> CommandResult:
        """Run boom command.

        Command Structure:
        The command starts with 'boom', followed by any global options from the
        configuration. Next comes the command (like 'entry', 'profile', or 'host'),
        then the subcommand (like 'create', 'delete', or 'list'). Finally, any
        command-specific options and positional arguments are added.

        Args:
            command: Command category (entry, profile, host)
            subcommand: Operation to perform (create, delete, list)
            action: Additional action (used by some commands)
            options: Command-specific options as key-value pairs
            positional_args: Additional arguments

        Returns:
            Command result

        Examples:
            List all boot entries:
            boom.run_command('entry', 'list')

            Create a profile:
            boom.run_command('profile', 'create',
                            options={'--name': 'Fedora'},
                            positional_args=['--os-version', '36'])

            Show specific entry:
            boom.run_command('entry', 'show',
                            options={'--boot-id': 'abcdef123'})
        """
        command_list: list[str] = [CLI_NAME]
        command_list.extend(self.config.to_args())

        if command is not None:
            command_list.append(command)
        if subcommand is not None:
            command_list.append(subcommand)
        if action is not None:
            command_list.append(action)
        if options is not None:
            for k, v in options.items():
                if v is None:
                    command_list.append(k)
                else:
                    command_list.extend((k, v))
        if positional_args:
            command_list.extend(positional_args)

        result = run(' '.join(command_list))
        if not result.succeeded:
            logging.error(f'Command failed: {result.stderr}')
        return result

    def get_version(self) -> CommandResult:
        """Get Boom version.

        Returns version information for:
        - Boom CLI tool
        - Associated libraries

        Returns:
            Version information

        Example:
            ```python
            Get version information:
            version = boom.version()
            ```
        """
        return self.run_command(positional_args=['--version'])


class Legacy(BoomBase):
    """Boom legacy bootloader support.

    Manages legacy bootloader configurations:
    - Writing boot entries to legacy formats
    - Clearing legacy configurations
    - Displaying boot entries in legacy formats

    Examples:
        Create with default configuration:
        legacy = Legacy()

        Create with custom configuration:
        legacy = Legacy(BoomConfig(verbose=2))
    """

    def write(self, boot_id: str | None = None) -> CommandResult:
        """Write boot entries to legacy bootloader configuration.

        Args:
            boot_id: Optional boot ID to write specific entry

        Returns:
            Command result

        Example:
            ```python
            Write all entries to legacy config:
            legacy.write()

            Write specific entry:
            legacy.write('abcdef123')
            ```
        """
        options = {}
        if boot_id:
            options['--boot-id'] = boot_id

        return self.run_command(command='legacy', subcommand='write', options=options)

    def clear(self) -> CommandResult:
        """Clear all Boom entries from legacy bootloader configuration.

        Returns:
            Command result

        Example:
            ```python
            Remove all boom entries from legacy config:
            legacy.clear()
            ```
        """
        return self.run_command('legacy', 'clear')

    def show(self, boot_id: str | None = None) -> CommandResult:
        """Show boot entries in legacy bootloader format.

        Args:
            boot_id: Optional boot ID to show specific entry

        Returns:
            Command result

        Example:
            ```python
            Show all entries in legacy format:
            legacy.show()

            Show specific entry:
            legacy.show('abcdef123')
            ```
        """
        options = {}
        if boot_id:
            options['--boot-id'] = boot_id

        return self.run_command(command='legacy', subcommand='show', options=options)


class Cache(BoomBase):
    """Boom boot image cache management.

    Manages the boot image cache:
    - List cached boot images
    - Display cache information

    Examples:
        Create with default configuration:
        cache = Cache()

        Create with custom configuration:
        cache = Cache(BoomConfig(verbose=1))
    """

    def list(self, img_id: str | None = None, linux: str | None = None, initrd: str | None = None) -> CommandResult:
        """List cache entries.

        Args:
            img_id: Optional image ID to filter
            linux: Filter by kernel path
            initrd: Filter by initramfs path

        Returns:
            Command result

        Example:
            ```python
            List all cache entries:
            cache.list()

            List specific image:
            cache.list(img_id='abc123')
            ```
        """
        options = {}
        if img_id:
            options['--image'] = img_id
        if linux:
            options['--linux'] = linux
        if initrd:
            options['--initrd'] = initrd

        return self.run_command(command='cache', subcommand='list', options=options)

    def show(self, img_id: str | None = None, linux: str | None = None, initrd: str | None = None) -> CommandResult:
        """Show cache entry details.

        Args:
            img_id: Optional image ID to show
            linux: Filter by kernel path
            initrd: Filter by initramfs path

        Returns:
            Command result

        Example:
            ```python
            Show cache entry details:
            cache.show(img_id='abc123')
            ```
        """
        options = {}
        if img_id:
            options['--image'] = img_id
        if linux:
            options['--linux'] = linux
        if initrd:
            options['--initrd'] = initrd

        return self.run_command(command='cache', subcommand='show', options=options)
