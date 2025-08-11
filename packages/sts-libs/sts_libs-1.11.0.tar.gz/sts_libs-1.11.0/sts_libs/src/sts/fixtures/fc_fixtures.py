# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""FC test fixtures."""

import logging
from pathlib import Path

import pytest

from sts.fc import FcDevice
from sts.multipath import MultipathDevice

MIN_PATHS = 2  # Minimum number of paths required for multipath setup
MAX_INTERVAL = 5  # Maximum wait interval in seconds
VERIFY_SIZE = '256k'  # Default size for verification data


@pytest.fixture(scope='class')
def get_fc_device() -> FcDevice:
    """Pytest fixture to get the first Fibre Channel (FC) device.

    Returns:
        The first FC device

    Example:
        ```Python
        def test_fc_device(get_fc_device: FcDevice):
            assert get_fc_device.path.exists()
        ```
    """
    devices = FcDevice.get_by_attribute('transport', 'fc:')
    # Break down complex assertion
    online_devices = [dev for dev in devices if dev.state == 'running']
    if not online_devices:
        pytest.skip("No online FC devices found with transport 'fc:'")
    return online_devices[0]


@pytest.fixture
def get_fc_paths(get_multipath_active_paths: tuple[MultipathDevice, list[dict]]) -> list[FcDevice]:
    """Fixture to get FC devices from multipath paths.

    Args:
        get_multipath_active_paths: Fixture providing multipath device and active paths

    Returns:
        List of FC devices for active paths

    Raises:
        pytest.skip: If no valid FC paths found
    """
    _, active_paths = get_multipath_active_paths
    fc_devices = []

    for path in active_paths:
        dev_name = path.get('dev')
        if not dev_name:
            continue
        try:
            fc_dev = FcDevice(name=dev_name)
            if fc_dev.path and Path(fc_dev.path).exists():
                fc_devices.append(fc_dev)
        except (ValueError, OSError) as e:
            logging.warning(f'Failed to get FC device for {dev_name}: {e}')

    if not fc_devices:
        pytest.skip('No valid FC paths found')

    return fc_devices


@pytest.fixture
def multipath_device_setup(
    get_multipath_active_paths: tuple[MultipathDevice, list[dict]], get_fc_paths: list[FcDevice]
) -> MultipathDevice:
    """Fixture to verify and provide multipath device setup.

    Args:
        get_multipath_active_paths: Fixture providing multipath device and paths
        get_fc_paths: Fixture providing FC devices

    Returns:
        MultipathDevice: Verified multipath device

    Raises:
        pytest.skip: If setup requirements not met
    """
    mpath_device, _ = get_multipath_active_paths
    fc_paths = get_fc_paths

    # Verify minimum paths requirement
    if len(fc_paths) < MIN_PATHS:
        pytest.skip(f'Need at least {MIN_PATHS} paths, found {len(fc_paths)}')

    # Verify device accessibility
    if not mpath_device.path or not Path(mpath_device.path).exists():
        pytest.skip(f'Multipath device {mpath_device.name} not accessible')

    return mpath_device
