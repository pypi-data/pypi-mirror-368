# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""snapm test fixtures.

This module provides fixtures for testing snapm (Snapshot Manager):
- Package installation and cleanup

Fixture Dependencies:
1. _snapm_test (base fixture)
   - Installs snapm packages
   - Logs system information

Error Handling:
- Package installation failures fail the test
"""

from __future__ import annotations

import logging

import pytest

from sts.utils.system import SystemManager

SNAPM_PACKAGE_NAME = 'snapm'


@pytest.fixture(scope='class')
def _snapm_test() -> None:
    """Set up snapm environment.

    This fixture provides the foundation for LVM testing:
    - Installs snapm utilities (snapm package)
    - Logs system information for debugging
    - Ensures consistent test environment

    Package Installation:
    - snapm: Core snapm utilities

    System Information:
    - Kernel version
    - snapm version

    Example:
        ```python
        @pytest.mark.usefixtures('_snapm_test')
        def test_snapm():
            # Test snapm snapsets and snapshot
            # Volumes are automatically cleaned up
        ```
    """
    system = SystemManager()
    assert system.package_manager.install(SNAPM_PACKAGE_NAME)
    logging.info(f'Kernel version: {system.info.kernel}')
