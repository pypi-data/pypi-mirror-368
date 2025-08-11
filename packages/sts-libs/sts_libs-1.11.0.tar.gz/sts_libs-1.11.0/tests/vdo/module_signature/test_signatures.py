# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import pytest

from sts.utils.cmdline import run
from sts.utils.system import SystemManager


@pytest.mark.usefixtures('_vdo_test')
def test_signatures() -> None:
    modules = ['kvdo']

    system = SystemManager()

    if system.info.distribution != 'rhel':
        pytest.skip('This test is only for RHEL releases')

    if system.info.version.major == '8':
        modules.append('uds')

    for module in modules:
        logging.info(f'Verifying signature for module: {module}')
        cr = run('keyctl list %:.builtin_trusted_keys')
        assert cr.succeeded
        logging.info(cr.stdout)
        signer = run(f'modinfo -F signer {module}')
        logging.info(f"Module '{module}' signer: {signer.stdout.strip()}")
        assert signer.succeeded
        assert signer.stdout.strip() in cr.stdout
        logging.info(f"Checking that module '{module}' is not loaded with errors")
        assert run(rf'grep "^{module}.*\(.*E.*\)$" /proc/modules').failed
