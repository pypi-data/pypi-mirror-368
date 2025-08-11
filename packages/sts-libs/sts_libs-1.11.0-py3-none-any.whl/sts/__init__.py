# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Storage Test Suite.

This module provides core functionality for storage testing:
- Host initialization
- Package management
- System configuration
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from testinfra import get_host

if TYPE_CHECKING:
    from testinfra.host import Host


class _HostManager:
    """Singleton host manager.

    Manages a single host instance for the entire test suite.
    This avoids the need for global variables while providing
    the same singleton functionality.
    """

    _instance: Host | None = None

    @classmethod
    def get_host(cls) -> Host:
        """Get singleton host instance.

        Returns:
            Host instance for local system
        """
        if cls._instance is None:
            cls._instance = get_host('local://')
        return cls._instance


def get_sts_host() -> Host:
    """Get singleton host instance.

    Returns:
        Host instance for local system

    Example:
        ```python
        from sts import get_sts_host

        host = get_sts_host()
        host.package('bash').is_installed
        True
        ```
    """
    return _HostManager.get_host()


__all__ = ['get_sts_host']
