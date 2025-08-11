# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Multipath fixtures module for the STS testing framework.

This module provides pytest fixtures for managing multipath devices during testing.
It includes fixtures for:
- Enabling multipath service and accessing multipath devices
- Disabling multipath service temporarily
- Accessing active paths of multipath devices

The fixtures handle proper setup and cleanup of multipath configurations to ensure
isolated and reliable testing environments.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from sts.multipath import MultipathDevice, MultipathService

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence


@pytest.fixture(scope='class')
def with_multipath_enabled() -> Generator[Sequence[MultipathDevice], None, None]:
    """Fixture to set up and tear down multipath devices.

    This fixture:
    1. Starts multipath service if not running
    2. Waits for service to be fully started
    3. Verifies multipath devices are accessible
    4. Handles cleanup on test completion

    Yields:
        list[MultipathDevice]: List of available multipath devices

    Raises:
        pytest.skip: If multipath service cannot be started or no devices found
    """
    mpath_service = MultipathService()
    was_stopped = not mpath_service.is_running()

    if was_stopped:
        logging.info('Starting multipath service...')
        if not mpath_service.start():
            pytest.skip('Failed to start multipath service')

    # Get multipath devices
    devices = MultipathDevice.get_all()
    if not devices:
        if was_stopped:
            mpath_service.stop()
        pytest.skip('No multipath devices found')

    yield devices

    # Cleanup only if we started the service
    if was_stopped:
        logging.info('Stopping multipath service...')
        mpath_service.stop()


@pytest.fixture(scope='class')
def with_multipath_disabled() -> Generator[None, None, None]:
    """Fixture to temporarily disable multipath service."""
    mpath_service = MultipathService()
    was_running = mpath_service.is_running()

    if was_running:
        logging.info('Temporarily disabling multipath service...')
        mpath_service.stop()

        # Flush devices after service is stopped
        if MultipathDevice.get_all():
            logging.warning('Flushing existing multipath devices...')
            if not mpath_service.flush():
                pytest.skip('Failed to flush multipath devices')

    yield

    if was_running:
        logging.info('Restoring multipath service...')
        mpath_service.start()


@pytest.fixture(scope='class')
def get_multipath_active_paths(
    with_multipath_enabled: Sequence[MultipathDevice],
) -> Generator[tuple[MultipathDevice, list[dict]], None, None]:
    """Fixture to get first multipath device with its active paths.

    Yields:
        tuple: (MultipathDevice, list of active path dictionaries)
              Each path dict contains: {'dev': device_name, 'dm_st': state, ...}

    Raises:
        pytest.skip: If no multipath device with active paths is found
    """
    mpath_devices = with_multipath_enabled
    if not mpath_devices:
        pytest.skip('No multipath devices found')

    # Find first device with active paths
    for device in mpath_devices:
        active_paths = [path for path in device.paths if path.get('dm_st') == 'active']
        if active_paths:
            device_path = Path(device.path) if device.path else None
            if device_path and device_path.exists():
                yield device, active_paths
                break
    else:
        pytest.skip('No multipath device with active paths found')
