# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""boom test fixtures.

This module provides fixtures for testing boom (boom-boot):
- Package installation and cleanup

Fixture Dependencies:
1. _boom_test (base fixture)
   - Installs boom package
   - Logs system information

Error Handling:
- Package installation failures fail the test
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from sts.boom.entry import BoomEntry
from sts.boom.host import BoomHost
from sts.boom.profile import BoomProfile
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from collections.abc import Generator

BOOM_PACKAGE_NAME = 'boom-boot'


@pytest.fixture(scope='class')
def _boom_test() -> None:
    """Set up boom test environment.

    This fixture provides the foundation for boom-boot testing:
    - Installs boom-boot package
    - Logs system information for debugging
    - Ensures consistent test environment

    Package Installation:
    - boom-boot: Core boom utilities

    System Information:
    - Kernel version

    Example:
        ```python
        @pytest.mark.usefixtures('_boom_test')
        def test_boom():
            # Test boom
        ```
    """
    system = SystemManager()
    if not system.package_manager.install(BOOM_PACKAGE_NAME):
        pytest.fail(f'Failed to install required package: {BOOM_PACKAGE_NAME}')
    logging.info(f'Kernel version: {system.info.kernel}')


@pytest.fixture
def profile_from_host() -> Generator[BoomProfile, None, None]:
    """Yields a BoomProfile instance created from host data.

    This fixture sets up a new BoomProfile instance and asserts its successful creation
    with 'from_host' parameter set to True. After the test uses the yielded profile, it
    ensures cleanup by calling the delete method on the profile.

    Example:
        ```python
        @pytest.mark.usefixtures('profile_from_host')
        def test_boom():
            profile = profile_from_host
        ```
    """
    profile = BoomProfile()
    if not profile.create(from_host=True):
        pytest.fail('Unable to create profile from host!')

    yield profile

    profile.delete()


@pytest.fixture
def default_host_profile(profile_from_host: BoomProfile) -> Generator[BoomHost, None, None]:
    """Yields a BoomHost instance created from Boom profile from host.

    This fixture sets up a new BoomHost instance and asserts its successful creation.
    After the test it ensures cleanup by calling the delete method on the Hostprofile.

    Example:
        ```python
        @pytest.mark.usefixtures('default_host_profile')
        def test_boom():
            host = default_host_profile
        ```
    """
    os_profile = profile_from_host
    host = BoomHost()
    assert host.create(profile_id=os_profile.os_id)
    assert host.host_id is not None

    yield host

    host.delete()


@pytest.fixture
def default_boom_entry(profile_from_host: BoomProfile) -> Generator[BoomEntry, None, None]:
    """Yields a BoomEntry instance created default boot entry.

    This fixture sets up a new BoomEntry instance by cloning the default entry and asserts its successful creation
    After the test it ensures cleanup by calling the delete method on cloned entry.

    Example:
        ```python
        @pytest.mark.usefixtures('default_boom_entry')
        def test_boom():
            entry = default_boom_entry
        ```
    """
    _ = profile_from_host
    entry = None
    entries = BoomEntry().get_all()
    if entries:
        entry = entries[0].clone()
    if not entry:
        pytest.fail('Unable to create a clone of the default Boom entry for tests')
    yield entry

    entry.delete()
