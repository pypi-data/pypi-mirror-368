# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Network-related errors.

This module defines exceptions for network operations:
- Interface errors (missing, invalid MAC)
- Connection errors (configuration, binding)
- NetworkManager errors (service, settings)
"""

from __future__ import annotations


class NetworkError(Exception):
    """Base class for network-related errors.

    Common error scenarios:
    - Invalid interface configuration
    - MAC address format issues
    - Missing network devices
    - Connection setup failures
    - NetworkManager service issues
    - IP address configuration errors

    Args:
        message: Error message describing what went wrong

    Example:
        ```python
        raise NetworkError('Invalid MAC address format')
        raise NetworkError('Interface eth0 not found')
        raise NetworkError('Failed to configure connection')
        ```
    """

    def __init__(self, message: str) -> None:
        """Initialize error.

        Args:
            message: Error message describing the failure
        """
        self.message = message
        super().__init__(self.message)
