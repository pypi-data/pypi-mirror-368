# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from time import sleep

import pytest

from sts.iscsi.iscsiadm import IscsiAdm


@pytest.mark.usefixtures('_iscsi_offload_setup')
def test_login_logout() -> None:
    iscsiadm = IscsiAdm()
    for i in range(1, 300):
        logging.info(f'Iteration {i}')
        assert iscsiadm.node_login().rc == 0
        sleep(0.1)
        assert iscsiadm.node_logoutall().rc == 0
