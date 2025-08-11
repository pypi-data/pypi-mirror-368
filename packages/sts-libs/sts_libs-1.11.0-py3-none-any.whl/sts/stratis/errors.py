# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Stratis-related errors.

This module defines exceptions for Stratis operations:
- Base error class
- Pool-specific errors
- Filesystem-specific errors
- Block device errors
"""

from __future__ import annotations


class StratisError(Exception):
    """Base class for Stratis-related errors.

    Used for:
    - General Stratis operations
    - Command execution failures
    - Configuration issues
    - Unexpected states

    Example:
        ```python
        raise StratisError('Failed to initialize Stratis')
        ```
    """

    def __init__(self, message: str) -> None:
        """Initialize error.

        Args:
            message: Error message describing the failure
        """
        self.message = message
        super().__init__(self.message)


class StratisPoolError(StratisError):
    """Error related to Stratis pool operations.

    Used for:
    - Pool creation failures
    - Pool destruction issues
    - Device addition problems
    - Encryption errors

    Example:
        ```python
        raise StratisPoolError('Failed to create pool: device in use')
        ```
    """


class StratisFilesystemError(StratisError):
    """Error related to Stratis filesystem operations.

    Used for:
    - Filesystem creation failures
    - Snapshot issues
    - Size limit problems
    - Mount failures

    Example:
        ```python
        raise StratisFilesystemError('Failed to create snapshot: no space')
        ```
    """


class StratisBlockdevError(StratisError):
    """Error related to Stratis blockdev operations.

    Used for:
    - Device initialization failures
    - Device addition problems
    - Device removal issues
    - Device state errors

    Example:
        ```python
        raise StratisBlockdevError('Failed to add device: already in use')
        ```
    """
