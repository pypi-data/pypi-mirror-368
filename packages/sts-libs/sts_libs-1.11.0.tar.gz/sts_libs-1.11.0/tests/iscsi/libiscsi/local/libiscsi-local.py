# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""libiscsi local tests.

This module tests libiscsi functionality using local targets:
- Basic iSCSI operations
- SCSI commands
- Error handling
"""

import os

import pytest

from sts.target import ACL, BackstoreFileio, create_basic_iscsi_target
from sts.utils.cmdline import run

TARGET_IQN = 'iqn.2023-11.com.sts:libiscsi'
INITIATOR1 = 'iqn.2007-10.com.github:sahlberg:libiscsi:iscsi-test'
INITIATOR2 = 'iqn.2007-10.com.github:sahlberg:libiscsi:iscsi-test-2'
USERID = os.getenv('LIBISCSI_CHAP_USERNAME')
PASSWORD = os.getenv('LIBISCSI_CHAP_PASSWORD')
MUTUAL_USERID = os.getenv('LIBISCSI_CHAP_TARGET_USERNAME')
MUTUAL_PASSWORD = os.getenv('LIBISCSI_CHAP_TARGET_PASSWORD')

# List of tests to run with libiscsi test suite
TESTS_TO_RUN = [
    'ALL.CompareAndWrite',
    'ALL.ExtendedCopy',
    'ALL.GetLBAStatus',
    'ALL.Inquiry',
    'ALL.Mandatory',
    'ALL.ModeSense6',
    'ALL.NoMedia',
    'ALL.OrWrite',
    'ALL.Prefetch10',
    'ALL.Prefetch16',
    'ALL.PreventAllow',
    'ALL.PrinReadKeys',
    'ALL.PrinServiceactionRange',
    'ALL.PrinReportCapabilities',
    'ALL.ProutRegister',
    'ALL.ProutReserve',
    'ALL.ProutClear',
    'ALL.ProutPreempt',
    'ALL.Read6',
    'ALL.Read10',
    'ALL.Read12',
    'ALL.Read16',
    'ALL.ReadCapacity10',
    'ALL.ReadCapacity16',
    'ALL.ReadDefectData10',
    'ALL.ReadDefectData12',
    'ALL.ReadOnly',
    'ALL.ReceiveCopyResults',
    'ALL.ReportSupportedOpcodes',
    # 'ALL.Reserve6', TODO fails on testing farm
    # 'ALL.Sanitize',
    'ALL.StartStopUnit',
    'ALL.TestUnitReady',
    'ALL.Unmap',
    'ALL.Verify10.Simple',
    'ALL.Verify10.BeyondEol',
    'ALL.Verify10.ZeroBlocks',
    # 'ALL.Verify10.VerifyProtect',
    'ALL.Verify10.Flags',
    # 'ALL.Verify10.Dpo',
    # 'ALL.Verify10.Mismatch',
    'ALL.Verify10.MismatchNoCmp',
    # 'ALL.Verify12', Not implemented in LIO
    'ALL.Verify16.Simple',
    'ALL.Verify16.BeyondEol',
    'ALL.Verify16.ZeroBlocks',
    'ALL.Verify16.Flags',
    'ALL.Verify16.MismatchNoCmp',
    'ALL.Write10',
    'ALL.Write12',
    'ALL.Write16',
    'ALL.WriteAtomic16',
    'ALL.WriteSame10',
    'ALL.WriteSame16',
    'ALL.WriteVerify10',
    'ALL.WriteVerify12',
    'ALL.WriteVerify16',
    'ALL.iSCSIcmdsn',
    'ALL.iSCSIdatasn',
    'ALL.iSCSIResiduals.Read*',
    'ALL.iSCSIResiduals.Write1*',
    'ALL.iSCSITMF',
    'ALL.iSCSISendTargets',
    'ALL.iSCSINop',
    'ALL.iSCSICHAP',
    'ALL.MultipathIO',
    'ALL.MultipathIO.Simple',
    'ALL.MultipathIO.Reset',
    'ALL.MultipathIO.CompareAndWrite',
    'ALL.MultipathIO.CompareAndWriteAsync',
]


@pytest.fixture(scope='class')
def _install_libiscsi_utils() -> None:
    """A pytest fixture to ensure that the `libiscsi-utils` package is installed."""
    libiscsi_repo = 'mhoyer/libiscsi'
    libiscsi_package = 'libiscsi-utils'

    result = run(f'rpm -q {libiscsi_package}')
    if result.failed:
        install_dnf_copr = run('sudo dnf install -y "dnf-command(copr)"')
        if install_dnf_copr.failed:
            pytest.skip(f'Failed to install dnf-command(copr):\n{install_dnf_copr.stderr}')
        copr_result = run(f'sudo dnf copr enable -y {libiscsi_repo}')
        if copr_result.failed:
            pytest.skip(f'Failed to enable {libiscsi_repo} repo:\n{copr_result.stderr}')
        install_result = run(f'sudo dnf install -y {libiscsi_package}')
        if install_result.failed:
            pytest.skip(f'Failed to install {libiscsi_package}:\n{install_result.stderr}')


@pytest.mark.usefixtures('_install_libiscsi_utils', 'iscsi_localhost_test')
class TestLibiscsiLocal:
    """Test libiscsi functionality using local targets."""

    def test_libiscsi_setup(self) -> None:
        """Set up iSCSI target for testing."""
        # Create target with first initiator
        assert create_basic_iscsi_target(
            target_wwn=TARGET_IQN,
            initiator_wwn=INITIATOR1,
            size='1G',
            userid=USERID,
            password=PASSWORD,
            mutual_userid=MUTUAL_USERID,
            mutual_password=MUTUAL_PASSWORD,
        ), 'Failed to create target'

        # Add second initiator with same auth
        acl = ACL(target_wwn=TARGET_IQN, initiator_wwn=INITIATOR2)
        acl.create_acl()
        if USERID and PASSWORD:
            acl.set_auth(
                userid=USERID,
                password=PASSWORD,
                mutual_userid=MUTUAL_USERID,
                mutual_password=MUTUAL_PASSWORD,
            )

        # Enable TPU emulation
        backstore = BackstoreFileio(name=INITIATOR1.split(':')[1])
        backstore.set_attribute('emulate_tpu', '1')

    @pytest.mark.parametrize('test', TESTS_TO_RUN)
    def test_libiscsi_test_cu(self, test: str) -> None:
        """Run libiscsi test suite.

        Args:
            test: Test name to run
        """
        result = run(f'iscsi-test-cu -d -n iscsi://127.0.0.1:3260/{TARGET_IQN}/0 -t {test}')
        assert result.succeeded, f'{test} test(s) have failed'
