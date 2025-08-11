# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base Stratis functionality.

This module provides base functionality for Stratis operations:
- Command execution
- Common utilities

Stratis is a storage management solution that provides:
- Advanced storage pools
- Thin provisioning
- Snapshots
- RAID support
- Encryption
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cached_property
from typing import Any, TypeVar, Union

from sts.stratis.errors import StratisError
from sts.utils.cmdline import CommandResult, run
from sts.utils.version import VersionInfo

CLI_NAME = 'stratis'

# Type definitions
T = TypeVar('T')
StratisOptions = dict[str, Union[str, None]]  # Command options
StratisReportData = dict[str, Union[str, list[dict[str, Any]]]]  # Report data


@dataclass
class StratisConfig:
    """Stratis configuration.

    Controls Stratis behavior:
    - Error handling: Whether to raise exceptions
    - UUID format: Hyphenated or not
    - Command execution: Global options

    Args:
        propagate: Whether to propagate errors as exceptions
        unhyphenated_uuids: Whether to use UUIDs without hyphens

    Examples:
        Create with default settings:
        stratis = StratisConfig()

        Create with error propagation:
        stratis = StratisConfig(propagate=True)
    """

    propagate: bool = False  # Raise exceptions on error
    unhyphenated_uuids: bool = False  # Use UUIDs without hyphens

    def to_args(self) -> list[str]:
        """Convert configuration to command arguments.

        Generates CLI options based on settings:
        - --propagate: Raise exceptions
        - --unhyphenated_uuids: Change UUID format

        Returns:
            List of command arguments

        Example:
            ```python
            Get command line arguments:
            config = StratisConfig(propagate=True)
            args = config.to_args()  # Returns ['--propagate']
            ```
        """
        args = []
        if self.propagate:
            args.append('--propagate')
        if self.unhyphenated_uuids:
            args.append('--unhyphenated_uuids')
        return args


class StratisBase:
    """Base class for Stratis operations.

    Provides common functionality:
    - Command execution with options
    - Error handling
    - Version information
    - System reporting

    Args:
        config: Stratis configuration (optional)

    Examples:
        Create with default configuration:
        stratis = StratisBase()

        Create with custom configuration:
        stratis = StratisBase(StratisConfig(propagate=True))
    """

    def __init__(self, config: StratisConfig | None = None) -> None:
        """Initialize Stratis base.

        Args:
            config: Stratis configuration
        """
        self.config = config or StratisConfig()

    @cached_property
    def version(self) -> VersionInfo:
        """Get Stratis version.

        Returns:
            Stratis version
        """
        return VersionInfo.from_string(self.run_command(action='--version').stdout.strip())

    def run_command(
        self,
        subcommand: str | None = None,
        action: str | None = None,
        options: StratisOptions | None = None,
        positional_args: list[str] | None = None,
    ) -> CommandResult:
        """Run stratis command.

        Command Structure:
        The command starts with 'stratis', followed by any global options from the
        configuration. Next comes the subcommand (like 'pool' or 'filesystem'),
        then the action (like 'create' or 'list'). Finally, any command-specific
        options and positional arguments are added.

        Args:
            subcommand: Command category (pool, filesystem, key)
            action: Operation to perform (list, create, set)
            options: Command-specific options as key-value pairs
            positional_args: Additional arguments

        Returns:
            Command result

        Examples:
            List all pools:
            stratis.run_command('pool', 'list')

            Create a filesystem:
            stratis.run_command('filesystem', 'create',
                              positional_args=['pool1', 'fs1'])

            Set encryption key:
            stratis.run_command('key', 'set',
                              options={'--keyfile-path': '/path/to/key'},
                              positional_args=['mykey'])
        """
        command_list: list[str] = [CLI_NAME]
        command_list.extend(self.config.to_args())

        if subcommand is not None:
            command_list.append(subcommand)
        if action is not None:
            command_list.append(action)
        if options is not None:
            command_list.extend(k if v is None else f'{k} {v}' for k, v in options.items())
        if positional_args:
            command_list.extend(positional_args)

        result = run(' '.join(command_list))
        if result.failed and self.config.propagate:
            raise StratisError(f'Command failed: {result.stderr}')
        return result

    def get_report(self) -> StratisReportData | None:
        """Get Stratis report.

        Retrieves system-wide information about:
        - Storage pools
        - Filesystems
        - Block devices
        - Cache devices

        Returns:
            Report data or None if failed

        Example:
            ```python
            Get system report:
            report = stratis.get_report()
            ```
        """
        result = self.run_command('report')
        if result.failed or not result.stdout:
            return None

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None


class Key(StratisBase):
    """Stratis key management.

    Manages encryption keys for:
    - Pool encryption
    - Data security
    - Access control

    Keys are identified by:
    - Key description (user-friendly name)
    - Key file path (contains actual key)

    Examples:
        Create with default configuration:
        key = Key()

        Create with error propagation:
        key = Key(StratisConfig(propagate=True))
    """

    def set(self, keydesc: str, keyfile_path: str) -> CommandResult:
        """Set key.

        Associates a key file with a description:
        - Key file must exist
        - Description must be unique
        - Used for pool encryption

        Args:
            keydesc: Key description (identifier)
            keyfile_path: Path to key file

        Returns:
            Command result

        Example:
            ```python
            Register encryption key:
            key.set('mykey', '/path/to/keyfile')
            ```
        """
        return self.run_command(
            'key',
            'set',
            options={'--keyfile-path': keyfile_path},
            positional_args=[keydesc],
        )

    def unset(self, keydesc: str) -> CommandResult:
        """Unset key.

        Removes key association:
        - Key must not be in use
        - Does not delete key file
        - Cannot undo operation

        Args:
            keydesc: Key description

        Returns:
            Command result

        Example:
            ```python
            Remove key registration:
            key.unset('mykey')
            ```
        """
        return self.run_command('key', 'unset', positional_args=[keydesc])

    def list(self) -> CommandResult:
        """List keys.

        Shows all registered keys:
        - Key descriptions only
        - No key file contents
        - No usage information

        Returns:
            Command result

        Example:
            ```python
            Show registered keys:
            key.list()
            ```
        """
        return self.run_command('key', 'list')

    def exists(self, keydesc: str) -> bool:
        """Check if key exists.

        Verifies key registration:
        - Checks key description
        - Does not verify key file
        - Does not check key validity

        Args:
            keydesc: Key description

        Returns:
            True if key exists, False otherwise

        Example:
            ```python
            Check key registration:
            exists = key.exists('mykey')
            ```
        """
        result = self.list()
        return bool(result.succeeded and keydesc in result.stdout)
