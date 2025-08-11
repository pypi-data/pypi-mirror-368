# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv
from pathlib import Path

from sts.utils.cmdline import run
from sts.utils.system import SystemManager

hca_id = getenv('RDMA_HCA_ID', 'mlx5_0')
port_id = getenv('RDMA_PORT', '1')


def test_pyverbs() -> None:
    """Run RDMA pyverbs tests."""
    system = SystemManager()
    assert system.package_manager.install('python3-pyverbs')
    test_bin = Path('/usr/share/doc/rdma-core/tests/run_tests.py')
    assert test_bin.is_file(), f'{test_bin} does not exist.'
    assert run(
        f'python {test_bin} --dev {hca_id} --port {port_id} -v',
    ).succeeded, f'{test_bin} test(s) have failed'
