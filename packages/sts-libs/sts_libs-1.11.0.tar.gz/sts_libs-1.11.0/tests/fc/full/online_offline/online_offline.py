# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""FC device online/offline tests.

This module tests:
1. Single FC device online/offline:
   - Cycles device offline/online
   - Verifies data integrity

2. Multipath FC device online/offline:
   - Cycles all paths offline/online
   - Verifies failover functionality
   - Ensures data integrity
"""

from __future__ import annotations

import logging
import random
import time
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from contextlib import AbstractContextManager

    from sts.fc import FcDevice
    from sts.multipath import MultipathDevice

import pytest

from sts.fio.fio import FIO

# Test parameters
ROUNDS = int(getenv('ROUNDS', '3'))
MAX_INTERVAL = 6
VERIFY_SIZE = '256k'
MIN_PATHS = 2


class VerifyData:
    """Handle writing and verifying test data."""

    def __init__(self, device_path: Path, size: str = VERIFY_SIZE) -> None:
        self.device_path = device_path
        self.size = size
        self.fio = FIO(device_path)
        self.fio.load_block_params()

    def write(self) -> bool:
        """Write test data pattern."""
        self.fio.update_parameters(
            {
                'size': self.size,
                'direct': '1',
                'rw': 'write',
                'ioengine': 'sync',
                'verify': 'crc32c',
            }
        )
        return self.fio.run()

    def verify(self) -> bool:
        """Verify written test data."""
        self.fio.update_parameters(
            {
                'size': self.size,
                'direct': '1',
                'rw': 'read',
                'verify': 'crc32c',
                'verify_fatal': '1',
                'verify_async': '1',
                'verify_backlog': '1',
            }
        )
        return self.fio.run()


def handle_device_state(device: FcDevice, state: str, path_verify: VerifyData, *, expect_verification: bool) -> None:
    """Handle device state changes and verification.

    Args:
        device: FC device to operate on
        state: Target state ('offline' or 'running')
        path_verify: Verification handler for individual path
        expect_verification: Expected verification result
    """
    action = 'Offlining' if state == 'offline' else 'Onlining'
    logging.info(f'{action} device {device.name}')

    # Change device state
    assert device.up_or_down_disk(state), f'Failed to set {device.name} {state}'
    device.wait_udev()

    # Wait random interval
    interval = random.randint(1, MAX_INTERVAL)
    logging.info(f'Waiting {interval}s while device is {state}')
    time.sleep(interval)

    # Verify path state
    if device.path and Path(device.path).exists():
        path_result = path_verify.verify()
        assert path_result == expect_verification, (
            f'Path verification {"failed" if expect_verification else "succeeded"} for {state} device {device.name}'
        )


@pytest.mark.usefixtures('with_multipath_disabled')
def test_offline_online(
    get_fc_device: FcDevice, timed_operation: Callable[[str], AbstractContextManager[None]]
) -> None:
    """Test single FC device offline/online cycles."""
    with timed_operation('FC device offline/online test'):
        fc_device = get_fc_device
        assert fc_device.path is not None, 'Device path is None'
        device_path = Path(fc_device.path)
        assert device_path.exists(), f'Device {device_path} not found'

        verify_data = VerifyData(device_path)

        with timed_operation('Initial data write'):
            assert verify_data.write(), 'Failed to write initial test data'

        for round_num in range(ROUNDS):
            with timed_operation(f'Round {round_num + 1}/{ROUNDS}'):
                handle_device_state(fc_device, 'offline', verify_data, expect_verification=False)
                handle_device_state(fc_device, 'running', verify_data, expect_verification=True)

        with timed_operation('Final verification'):
            assert verify_data.verify(), 'Final data verification failed'


@pytest.mark.usefixtures('with_multipath_enabled')
def test_multipath_paths_offline_online(
    multipath_device_setup: MultipathDevice,
    get_fc_paths: list[FcDevice],
    timed_operation: Callable[[str], AbstractContextManager[None]],
) -> None:
    """Test multipath device path offline/online cycles."""
    with timed_operation('Multipath offline/online test'):
        mpath_device = multipath_device_setup
        assert mpath_device.path is not None, f'Multipath device path not found: {mpath_device}'
        device_path = Path(mpath_device.path)
        mpath_verify = VerifyData(device_path)

        # Create path verifiers
        path_verifiers = {}
        for path in get_fc_paths:
            if path.path:
                path_verifiers[path.name] = VerifyData(Path(path.path))

        with timed_operation('Initial data write'):
            assert mpath_verify.write(), 'Failed to write initial test data'
            # Write test data to each path
            for verifier in path_verifiers.values():
                assert verifier.write(), 'Failed to write initial path test data'

        for round_num in range(ROUNDS):
            with timed_operation(f'Round {round_num + 1}/{ROUNDS}'):
                # Offline all paths
                for path in get_fc_paths:
                    if verifier := path_verifiers.get(path.name):
                        handle_device_state(path, 'offline', verifier, expect_verification=False)

                # Online all paths
                for path in get_fc_paths:
                    if verifier := path_verifiers.get(path.name):
                        handle_device_state(path, 'running', verifier, expect_verification=True)

        with timed_operation('Final verification'):
            assert mpath_verify.verify(), 'Final multipath verification failed'
            # Verify each path
            for name, verifier in path_verifiers.items():
                assert verifier.verify(), f'Final path verification failed for {name}'
