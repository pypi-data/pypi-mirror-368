# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Command execution module.

This module provides functionality for command execution:
- Command running
- Command argument handling
- Command validation
"""

from __future__ import annotations

import logging
from typing import TypedDict, Union

from testinfra.backend.base import CommandResult

from sts import get_sts_host

host = get_sts_host()


# Re-export CommandResult for convenience
__all__ = ['CommandResult']

# Type for command argument values
ArgValue = Union[str, int, float, bool, list[str], list[int], list[float], None]


class CommandArgs(TypedDict, total=False):
    """Command arguments type.

    This type represents command arguments that can be passed to format_args.
    The values can be strings, numbers, booleans, lists, or None.
    """

    # Allow any string key with ArgValue type
    __extra__: ArgValue


def run(cmd: str, msg: str | None = None) -> CommandResult:
    """Run command and return result.

    This is a thin wrapper around testinfra's run() that adds logging.

    Args:
        cmd: Command to execute
        msg: Optional message to log before execution

    Returns:
        CommandResult from testinfra

    Example:
        ```python
        result = run('ls -l')
        assert result.succeeded
        print(result.stdout)
        ```
    """
    msg = msg or 'Running'
    logging.info(f"{msg}: '{cmd}'")
    return host.run(cmd)


def format_arg(key: str, value: ArgValue) -> str:
    """Format command argument.

    Args:
        key: Argument name
        value: Argument value (str, int, float, bool, list, or None)

    Returns:
        Formatted argument string

    Example:
        ```python
        format_arg('size', '1G')
        '--size=1G'
        format_arg('quiet', True)
        '--quiet'
        format_arg('count', 5)
        '--count=5'
        ```
    """
    key = key.replace('_', '-')
    if value is True:
        return f'--{key}'
    if value is False or value is None:
        return ''
    if isinstance(value, list):
        return ' '.join(f"--{key}='{v}'" for v in value)
    return f"--{key}='{value}'"


def format_args(**kwargs: ArgValue) -> str:
    """Format command arguments.

    Args:
        **kwargs: Command arguments (str, int, float, bool, list, or None)

    Returns:
        Formatted arguments string

    Example:
        ```python
        format_args(size='1G', quiet=True, count=5)
        '--size=1G --quiet --count=5'
        ```
    """
    args = []
    for key, value in kwargs.items():
        if arg := format_arg(key, value):
            args.append(arg)
    return ' '.join(args)


def exists(cmd: str) -> bool:
    """Check if command exists in PATH.

    This is a direct passthrough to testinfra's exists().

    Args:
        cmd: Command to check

    Returns:
        True if command exists in PATH

    Example:
        ```python
        assert exists('ls')
        ```
    """
    return host.exists(cmd)
