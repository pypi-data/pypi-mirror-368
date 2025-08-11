# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import pytest

from sts import get_sts_host, target
from sts.iscsi.config import set_initiatorname
from sts.iscsi.iscsiadm import IscsiAdm
from sts.iscsi.session import IscsiSession
from sts.utils.cmdline import run

host = get_sts_host()


@pytest.mark.usefixtures('iscsi_localhost_test')
def test_many_luns_local() -> None:
    n_luns: int = 256
    back_size: str = '1M'
    t_iqn: str = 'iqn.1994-05.com.redhat:manylunstarget'
    i_iqn: str = 'iqn.1994-05.com.redhat:manylunsinitiator'

    # Create target and ACL
    iscsi_target = target.Iscsi(target_wwn=t_iqn)
    assert iscsi_target.create_target().succeeded
    acl = target.ACL(target_wwn=t_iqn, initiator_wwn=i_iqn)
    assert acl.create_acl().succeeded

    # Create backstores and LUNs
    for n in range(n_luns):
        backstore = target.BackstoreFileio(name=f'backstore{n}')
        assert backstore.create_backstore(size=back_size, file_or_dev=f'backstore_file{n}').succeeded
        assert target.IscsiLUN(target_wwn=t_iqn).create_lun(storage_object=backstore.path).succeeded

    # Setup initiator and test
    set_initiatorname(i_iqn)
    iscsiadm = IscsiAdm()
    assert iscsiadm.discovery(portal='127.0.0.1', type='st').succeeded

    for _ in range(3):
        assert iscsiadm.node_login()
        # TODO: Replace wait_udev with proper udev event handling
        # wait_udev(sleeptime=1)
        sessions = IscsiSession.get_all()
        test_session = next(s for s in sessions if s.target_iqn == t_iqn)
        disks = test_session.get_disks()
        assert disks is not None

        # Check targetcli version for expected disk count
        targetcli = host.package('targetcli')  # type: ignore[reportUnknownMemberType]
        expected_disks = (
            255
            if targetcli.is_installed  # type: ignore[attr-defined]
            and targetcli.version < '2.1.54'  # type: ignore[attr-defined]
            else n_luns
        )
        assert len(disks) == expected_disks

        for disk in disks:
            assert disk.is_running
        assert iscsiadm.node_logoutall()

    # Running clearconfig manually to avoid individually deleting backstores
    run('targetcli clearconfig confirm=true')

    # Clean up backstore files
    for n in range(n_luns):
        Path(f'backstore_file{n}').unlink(missing_ok=True)
