# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pytest configuration for sts-based tests."""

import logging
from collections.abc import Generator
from os import getenv
from typing import Any

import pytest

from sts.iscsi.config import IscsiConfig, IscsiInterface, IscsiNode, setup

pytest_plugins = [
    'sts.fixtures.iscsi_fixtures',
    'sts.fixtures.rdma_fixtures',
    'sts.fixtures.stratis_fixtures',
    'sts.fixtures.common_fixtures',
    'sts.fixtures.lvm_fixtures',
    'sts.fixtures.target_fixtures',
    'sts.fixtures.fc_fixtures',
    'sts.fixtures.snapm_fixtures',
    'sts.fixtures.module_fixtures',
    'sts.fixtures.boom_fixtures',
    'sts.fixtures.nvme_fixtures',
    'sts.fixtures.multipath_fixtures',
]


@pytest.fixture(scope='class')
def _iscsi_offload_setup(_iscsi_test: Generator[Any, None, None]) -> None:
    """Set up iSCSI offload environment."""
    iscsi_env = getenv('ISCSI_SETUP_VARS')

    be2iscsi_vars = IscsiConfig(
        initiatorname='iqn.1994-05.com.redhat:storageqe-84',
        ifaces=[
            IscsiInterface(
                iscsi_ifacename='be2iscsi.00:90:fa:d6:bc:ed.ipv4.0',
                ipaddress='172.16.1.84',
            ),
        ],
        targets=[
            IscsiNode(
                target_iqn='iqn.2003-01.org.linux-iscsi.target',
                portal='172.16.1.10:3260',
                interface='be2iscsi.00:90:fa:d6:bc:ed.ipv4.0',
            ),
        ],
        driver='be2iscsi',
    )

    bnx2i_vars = IscsiConfig(
        initiatorname='iqn.1994-05.com.redhat:storageqe-83',
        ifaces=[
            IscsiInterface(
                iscsi_ifacename='bnx2i.ac:16:2d:85:64:bd',
                ipaddress='172.16.1.83',
            ),
        ],
        targets=[
            IscsiNode(
                target_iqn='iqn.2003-01.org.linux-iscsi.target',
                portal='172.16.1.10:3260',
                interface='bnx2i.ac:16:2d:85:64:bd',
            ),
        ],
        driver='bnx2i',
    )

    cxgb4i_vars = IscsiConfig(
        initiatorname='iqn.1994-05.com.redhat:storageqe-87',
        ifaces=[
            IscsiInterface(
                iscsi_ifacename='cxgb4i.00:07:43:73:04:b8.ipv4.0',
                ipaddress='172.16.1.87',
            ),
        ],
        targets=[
            IscsiNode(
                target_iqn='iqn.2003-01.org.linux-iscsi.target',
                portal='172.16.1.10:3260',
                interface='cxgb4i.00:07:43:73:04:b8.ipv4.0',
            ),
        ],
        driver='cxgb4i',
    )

    intel_vars = IscsiConfig(
        initiatorname='iqn.1994-05.com.redhat:storageqe-82',
        ifaces=[
            IscsiInterface(
                iscsi_ifacename='intel-e810-p1',
                ipaddress='172.16.1.82',
                hwaddress='b4:96:91:a0:68:8b',
            ),
        ],
        targets=[
            IscsiNode(
                target_iqn='iqn.2003-01.org.linux-iscsi.target',
                portal='172.16.1.10:3260',
                interface='intel-e810-p1',
            ),
        ],
        driver='iscsi_tcp',
    )

    qedi_vars = IscsiConfig(
        initiatorname='iqn.1994-05.com.redhat:storageqe-86',
        ifaces=[
            IscsiInterface(
                iscsi_ifacename='qedi.00:0e:1e:f1:9c:f1',
                ipaddress='172.16.1.86',
            ),
        ],
        targets=[
            IscsiNode(
                target_iqn='iqn.2003-01.org.linux-iscsi.target',
                portal='172.16.1.10:3260',
                interface='qedi.00:0e:1e:f1:9c:f1',
            ),
        ],
        driver='qedi',
    )

    vars_mapping = {
        'intel': intel_vars,
        'qedi': qedi_vars,
        'cxgb4i': cxgb4i_vars,
        'cxgb4i_noipv4': cxgb4i_vars,
        'be2iscsi': be2iscsi_vars,
        'bnx2i': bnx2i_vars,
    }

    if not iscsi_env:
        logging.error('_iscsi_offload_setup requires ISCSI_SETUP_VARS')
        return

    try:
        vars_to_set = vars_mapping[iscsi_env]
    except KeyError as err:
        raise ValueError(f'Unsupported ISCSI_SETUP_VARS value: {iscsi_env}') from err

    if iscsi_env == 'cxgb4i_noipv4':
        vars_to_set.ifaces[0].iscsi_ifacename = 'cxgb4i.00:07:43:73:04:b8'

    # Set up iSCSI
    setup(vars_to_set)
