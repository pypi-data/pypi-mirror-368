# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for iSCSI parameter validation.

This module tests the parameter validation functions:
- Header digest
- Data segment lengths
- Burst lengths
- Immediate data
- Initial R2T
"""

from __future__ import annotations

import pytest

from sts.iscsi.parameters import verify_parameter


@pytest.mark.parametrize(
    ('param', 'target', 'initiator', 'negotiated', 'max_burst_length', 'expected'),
    [
        # HeaderDigest tests
        ('HeaderDigest', 'CRC32C', 'CRC32C', 'CRC32C', None, True),
        ('HeaderDigest', 'None', 'None', 'None', None, True),
        ('HeaderDigest', 'None', 'CRC32C', 'None', None, True),
        ('HeaderDigest', 'CRC32C', 'None', 'None', None, True),
        ('HeaderDigest', 'CRC32C,None', 'CRC32C,None', 'CRC32C', None, True),
        ('HeaderDigest', 'None,CRC32C', 'None,CRC32C', 'None', None, True),
        ('HeaderDigest', 'CRC32C,None', 'None,CRC32C', 'None', None, True),
        ('HeaderDigest', 'None,CRC32C', 'CRC32C,None', 'CRC32C', None, True),
        # MaxRecvDataSegmentLength tests
        ('MaxRecvDataSegmentLength', '512', '1024', '1024', None, True),
        ('MaxRecvDataSegmentLength', '1024', '512', '512', None, True),
        # MaxXmitDataSegmentLength tests
        ('MaxXmitDataSegmentLength', '512', '1024', '512', None, True),
        ('MaxXmitDataSegmentLength', '1024', '512', '512', None, True),
        # MaxBurstLength tests
        ('MaxBurstLength', '512', '1024', '512', None, True),
        ('MaxBurstLength', '1024', '512', '512', None, True),
        # ImmediateData tests
        ('ImmediateData', 'Yes', 'Yes', 'Yes', None, True),
        ('ImmediateData', 'Yes', 'No', 'No', None, True),
        ('ImmediateData', 'No', 'Yes', 'No', None, True),
        ('ImmediateData', 'No', 'No', 'No', None, True),
        # InitialR2T tests
        ('InitialR2T', 'No', 'No', 'No', None, True),
        ('InitialR2T', 'Yes', 'No', 'Yes', None, True),
        ('InitialR2T', 'No', 'Yes', 'Yes', None, True),
        ('InitialR2T', 'Yes', 'Yes', 'Yes', None, True),
        # FirstBurstLength tests
        ('FirstBurstLength', '512', '1024', '512', None, True),
        ('FirstBurstLength', '1024', '512', '512', None, True),
        ('FirstBurstLength', '2048', '1024', '1024', ('1024', '2048'), True),
        ('FirstBurstLength', '2048', '1024', '2048', None, False),
    ],
)
def test_verify_parameter(
    param: str,
    target: str,
    initiator: str,
    negotiated: str,
    max_burst_length: tuple[str, str] | None,
    expected: bool,
) -> None:
    """Test parameter validation.

    This test:
    1. Tests various combinations of parameters and values
    2. Verifies validation result matches expected result

    Args:
        param: Parameter name
        target: Target value
        initiator: Initiator value
        negotiated: Negotiated value
        max_burst_length: MaxBurstLength values for FirstBurstLength validation
        expected: Expected validation result
    """
    assert verify_parameter(param, target, initiator, negotiated, max_burst_length) == expected


def test_invalid_parameter() -> None:
    """Test validation of invalid parameter."""
    assert not verify_parameter('InvalidParam', 'value', 'value', 'value')
