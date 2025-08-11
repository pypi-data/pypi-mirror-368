# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests iSCSI parameters negotiation with iscsiadm, targetcli.

This module tests parameter negotiation between initiator and target:
- Header digest
- Data segment lengths
- Burst lengths
- Immediate data
- Initial R2T
"""

from __future__ import annotations

import logging
from itertools import product

import pytest

from sts.fio.fio import FIO
from sts.iscsi.config import IscsidConfig, IscsiNode
from sts.iscsi.parameters import PARAM_MAP, verify_parameter
from sts.iscsi.session import IscsiSession
from sts.multipath import MultipathDevice, MultipathService
from sts.scsi import ScsiDevice
from sts.target import Iscsi

# Test configuration
TARGET_IQN = 'iqn.2024-01.sts.params-target'
INITIATOR_IQN = 'iqn.2024-01.sts.params-client'

# Parameter pools
DIGEST_POOL = [
    'None',
    'CRC32C',
    'None,CRC32C',
    'CRC32C,None',
]
YESNO_POOL = ['Yes', 'No']
BYTE_POOL = [
    '512',
    '16777212',
]


def do_io(device: str) -> bool:
    """Run I/O test on device.

    Args:
        device: Device path

    Returns:
        True if successful, False otherwise
    """
    fio = FIO(filename=device)
    fio.update_parameters({'runtime': '120'})  # 2 minute cap
    return fio.run()


def get_test_device() -> str:
    """Get device to test.

    Returns:
        Device path

    Raises:
        AssertionError: If no device found
    """
    # Try multipath first
    mp_service = MultipathService()
    if mp_service.is_running():
        devices = MultipathDevice.get_all()
        if devices and devices[0].path:
            return str(devices[0].path)

    # Fall back to SCSI
    devices = ScsiDevice.get_by_vendor('LIO-ORG')
    assert devices
    assert devices[0].path, 'Could not find device to use'
    return str(devices[0].path)


@pytest.mark.parametrize('iscsi_target', [{'size': '256M'}], indirect=True)
def test_parameters(iscsi_target: IscsiNode) -> None:
    """Test iSCSI parameter negotiation.

    This test:
    1. Sets various parameter combinations on target and initiator
    2. Verifies parameter negotiation
    3. Runs I/O test to verify functionality

    Args:
        iscsi_target: iSCSI target fixture
    """
    # Get target IQN from node
    target_iqn = iscsi_target.target_iqn
    assert target_iqn is not None

    # Create target instance for parameter setting
    target = Iscsi(target_wwn=target_iqn)

    # Generate parameter combinations
    r = 2  # repeat - initiator, target = 2
    digest_cartesian = list(product(DIGEST_POOL, repeat=r))
    # Prevent 'CRC32C'+'None'
    digest_cartesian = [p for p in digest_cartesian if p not in {('None', 'CRC32C'), ('CRC32C', 'None')}]
    yesno_cartesian = list(product(YESNO_POOL, repeat=r)) * 4
    byte_cartesian = list(product(BYTE_POOL, repeat=r)) * 4

    # Test parameter combinations
    iterations = 14
    for i in range(iterations):
        logging.info(f'Iteration {i}')

        # Set target parameters
        target_params = {
            'HeaderDigest': digest_cartesian[i][0],
            'MaxRecvDataSegmentLength': byte_cartesian[i][0],
            'MaxXmitDataSegmentLength': byte_cartesian[-i][0],
            'MaxBurstLength': byte_cartesian[-i][0],
            'FirstBurstLength': byte_cartesian[i][0],
            'ImmediateData': yesno_cartesian[i][0],
            'InitialR2T': yesno_cartesian[-i][0],
        }
        for param, value in target_params.items():
            target.set_parameter(param, value)

        # Set initiator parameters
        initiator_params = {
            'node.conn[0].iscsi.HeaderDigest': digest_cartesian[i][1],
            'node.conn[0].iscsi.MaxRecvDataSegmentLength': byte_cartesian[i][1],
            'node.conn[0].iscsi.MaxXmitDataSegmentLength': byte_cartesian[~i][1],
            'node.session.iscsi.MaxBurstLength': byte_cartesian[~i][1],
            'node.session.iscsi.FirstBurstLength': byte_cartesian[i][1],
            'node.session.iscsi.ImmediateData': yesno_cartesian[i][1],
            'node.session.iscsi.InitialR2T': yesno_cartesian[~i][1],
        }
        config = IscsidConfig()
        config.set_parameters(initiator_params)
        config.save()

        # Logout and login to apply parameters
        iscsi_target.logout()
        iscsi_target.login()

        # Get negotiated parameters
        sessions = IscsiSession.get_all()
        assert sessions, 'No iSCSI sessions found'
        session = sessions[0]
        negotiated = session.get_data_p2()

        # Verify parameters
        for param in PARAM_MAP:
            target_value = target_params[param]
            initiator_value = initiator_params[PARAM_MAP[param]]
            negotiated_value = negotiated[param]

            logging.info(
                f'{param}: Target: {target_value} | Initiator: {initiator_value} | Negotiated: {negotiated_value}',
            )

            # Special handling for FirstBurstLength
            max_burst_length = None
            if param == 'FirstBurstLength':
                max_burst_length = (
                    target_params['MaxBurstLength'],
                    initiator_params[PARAM_MAP['MaxBurstLength']],
                )
            assert verify_parameter(param, target_value, initiator_value, negotiated_value, max_burst_length), (
                f'Negotiated parameter {param} has unexpected value'
            )

        # Run I/O test
        device = get_test_device()
        assert do_io(device), 'I/O test failed'
