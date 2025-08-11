# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""FIO-related errors.

This module defines exceptions for FIO operations:
- Configuration errors (invalid parameters, file issues)
- Execution errors (runtime failures, system issues)
- Base error class for common functionality
"""

from __future__ import annotations


class FIOError(Exception):
    """Base class for FIO-related errors.

    Common error scenarios:
    - Invalid parameter combinations
    - Missing required files/devices
    - System resource issues
    - Runtime failures

    Args:
        message: Error message describing the failure

    Example:
        ```python
        raise FIOError('Failed to initialize FIO test')
        ```
    """

    def __init__(self, message: str) -> None:
        """Initialize error.

        Args:
            message: Error message describing what went wrong
        """
        self.message = message
        super().__init__(self.message)


class FIOConfigError(FIOError):
    """Error related to FIO configuration.

    Configuration errors include:
    - Invalid parameter values
    - Missing required parameters
    - Invalid config file format
    - File permission issues
    - Invalid parameter combinations

    Example:
        ```python
        raise FIOConfigError('Invalid block size: must be power of 2')
        raise FIOConfigError('Config file not found: test.fio')
        ```
    """


class FIOExecutionError(FIOError):
    """Error related to FIO execution.

    Execution errors include:
    - FIO binary not found
    - Insufficient permissions
    - Device/file access issues
    - Resource limits (memory, file descriptors)
    - System call failures
    - Verification failures

    Example:
        ```python
        raise FIOExecutionError('Failed to open target device: permission denied')
        raise FIOExecutionError('Verification failed: CRC mismatch')
        ```
    """
