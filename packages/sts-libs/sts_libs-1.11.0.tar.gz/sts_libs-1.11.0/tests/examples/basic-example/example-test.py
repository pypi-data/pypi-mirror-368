# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import pytest

from sts.fio.fio import FIO
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [1], indirect=True)
def test_example(loop_devices: list[str]) -> None:
    """Test example using sts-libs features.

    This test:
    1. Uses loop_devices fixture to get a test device
    2. Verifies device exists using run()
    3. Runs I/O test using FIO
    """
    device = loop_devices[0]
    logging.info(f'Starting example test with device {device}')

    # Verify device exists
    result = run(f'lsblk {device}')
    assert result.succeeded, 'lsblk command failed for some reason'
    assert device.split('/')[-1] in result.stdout

    # Run I/O test
    fio = FIO(filename=device)
    assert fio.run()
