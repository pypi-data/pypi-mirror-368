# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Snapshot Manager base functionality.

This module provides base functionality for Snapshot Manager operations:
- Command execution
- Package management
- Common utilities
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any

from sts.utils.cmdline import CommandResult, run
from sts.utils.version import VersionInfo

if TYPE_CHECKING:
    from collections.abc import Sequence

# Type aliases
SnapmOptions = dict[str, Any]  # Command options

# Constants
CLI_NAME = 'snapm'
PACKAGE_NAME = 'snapm'


@dataclass
class SnapmBase:
    """Base class for Snapshot Manager operations.

    Provides common functionality:
    - Command execution with options
    - Package installation
    - Debugging support

    Args:
        debugopts: Debug options to pass to snapm commands
        verbose: Whether to enable verbose output

    Examples:
        Create with default configuration:
        snapm = SnapmBase()

        Create with debug options:
        snapm = SnapmBase(debugopts=['--debug-opt1', '--debug-opt2'])
    """

    debugopts: list[str] | None = None
    verbose: bool = False

    def run_command(
        self,
        subcommand: str | None = None,
        action: str | None = None,
        options: SnapmOptions | None = None,
        positional_args: Sequence[str] | None = None,
    ) -> CommandResult:
        """Run snapm command.

        Command Structure:
        The command starts with 'snapm', followed by any global options.
        Next comes the subcommand (like 'snapset' or 'snapshot'),
        then the action (like 'create' or 'activate'). Finally, any
        command-specific options and positional arguments are added.

        Args:
            subcommand: Command category (snapset, snapshot)
            action: Operation to perform (create, activate, deactivate)
            options: Command-specific options as key-value pairs
                     Example: {'--name': 'my_snapset', '--json': None}
            positional_args: Additional arguments that follow the options
                     Example: ['snapset_name', '/mount/point']

        Returns:
            CommandResult object containing stdout, stderr, and status

        Examples:
            List all snapsets:
            snapm.run_command('snapset', 'list')

            Create a snapset:
            snapm.run_command('snapset', 'create',
                             positional_args=['name', '/mount/point'])

            Delete a specific snapset:
            snapm.run_command('snapset', 'delete', options={'--name': 'my_snapset'})
        """
        command_list: list[str] = [CLI_NAME]

        # Add global options
        if self.verbose:
            command_list.append('--verbose')
        if self.debugopts:
            command_list.extend(self.debugopts)

        # Add subcommand and action
        if subcommand is not None:
            command_list.append(subcommand)
        if action is not None:
            command_list.append(action)

        # Add options
        if options is not None:
            command_list.extend(k if v is None else f'{k} {v}' for k, v in options.items())

        # Add positional arguments
        if positional_args:
            command_list.extend(positional_args)

        command = ' '.join(command_list)
        result = run(command)
        if result.failed:
            logging.debug(f'Snapm command failed: {command}')
            logging.debug(f'Error: {result.stderr}')
        return result

    @cached_property
    def version(self) -> VersionInfo:
        """Get Stratis version.

        Returns:
            Stratis version
        """
        return VersionInfo.from_string(self.run_command(options={'--version': None}).stdout.strip())
