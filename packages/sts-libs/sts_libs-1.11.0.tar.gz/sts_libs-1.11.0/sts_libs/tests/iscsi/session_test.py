# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test iSCSI session management.

This module tests:
- Session discovery
- Session information
- Session operations
"""

from typing import Any
from unittest.mock import patch

import pytest

from sts.iscsi.session import IscsiSession


@pytest.fixture
def mock_session() -> IscsiSession:
    """Create mock iSCSI session.

    Returns:
        IscsiSession instance
    """
    return IscsiSession(
        session_id='1',
        target_iqn='iqn.2003-01.org.linux-iscsi:target1',
        portal='192.168.1.100:3260',
    )


def test_session_init(mock_session: IscsiSession) -> None:
    """Test session initialization.

    Args:
        mock_session: Mock session instance
    """
    assert mock_session.session_id == '1'
    assert mock_session.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'
    assert mock_session.portal == '192.168.1.100:3260'


def test_session_logout(mock_session: IscsiSession, mock_command_result: Any) -> None:
    """Test session logout.

    Args:
        mock_session: Mock session instance
        mock_command_result: Mock command result fixture
    """
    # Test successful logout
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.node_logout.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        assert mock_session.logout()
        mock_iscsiadm.node_logout.assert_called_once()

    # Test failed logout
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.node_logout.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_session.logout()


def test_session_get_data(mock_session: IscsiSession, mock_command_result: Any) -> None:
    """Test getting session data.

    Args:
        mock_session: Mock session instance
        mock_command_result: Mock command result fixture
    """
    # Test successful data retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(
            rc=0,
            stdout='node.session.auth.authmethod = None\nnode.session.auth.username = \n',
            stderr='',
            command='',
        )
        data = mock_session.get_data()
        assert data == {
            'node.session.auth.authmethod': 'None',
            'node.session.auth.username': '',
        }

    # Test failed data retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_session.get_data()


def test_session_get_data_p2(mock_session: IscsiSession, mock_command_result: Any) -> None:
    """Test getting session data with print level 2.

    Args:
        mock_session: Mock session instance
        mock_command_result: Mock command result fixture
    """
    # Test successful data retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(
            rc=0,
            stdout='Target: iqn.2003-01.org.linux-iscsi:target1\nCurrent Portal: 192.168.1.100:3260,1\n',
            stderr='',
            command='',
        )
        data = mock_session.get_data_p2()
        assert data == {
            'Target': 'iqn.2003-01.org.linux-iscsi:target1',
            'Current Portal': '192.168.1.100:3260,1',
        }

    # Test failed data retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_session.get_data_p2()


def test_session_disk_is_running() -> None:
    """Test session disk state."""
    disk = IscsiSession.SessionDisk(
        name='sda',
        state='running',
        scsi_n='1',
        channel='0',
        id='0',
        lun='0',
    )
    assert disk.is_running()

    disk = IscsiSession.SessionDisk(
        name='sda',
        state='error',
        scsi_n='1',
        channel='0',
        id='0',
        lun='0',
    )
    assert not disk.is_running()


def test_session_get_disks(mock_session: IscsiSession, mock_command_result: Any) -> None:
    """Test getting session disks.

    Args:
        mock_session: Mock session instance
        mock_command_result: Mock command result fixture
    """
    # Test successful disk retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(
            rc=0,
            stdout='\t\tscsi2 Channel 00 Id 0 Lun: 0\n\t\t\tAttached scsi disk sda State: running\n',
            stderr='',
            command='',
        )
        disks = mock_session.get_disks()
        assert len(disks) == 1
        assert disks[0].name == 'sda'
        assert disks[0].state == 'running'
        assert disks[0].scsi_n == '2'
        assert disks[0].channel == '00'
        assert disks[0].id == '0'
        assert disks[0].lun == '0'

    # Test failed disk retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_session.get_disks()


def test_session_get_all(mock_command_result: Any) -> None:
    """Test getting all sessions.

    Args:
        mock_command_result: Mock command result fixture
    """
    # Test successful session retrieval
    with patch('sts.iscsi.session.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.session.return_value = mock_command_result(
            rc=0,
            stdout='tcp: [1] 192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target1\ntcp: [2] 192.168.1.101:3260,1 iqn.2003-01.org.linux-iscsi:target2\n',
            stderr='',
            command='',
        )
        sessions = IscsiSession.get_all()
        assert len(sessions) == 2
        assert sessions[0].session_id == '1'
        assert sessions[0].portal == '192.168.1.100:3260'
        assert sessions[0].target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'
        assert sessions[1].session_id == '2'
        assert sessions[1].portal == '192.168.1.101:3260'
        assert sessions[1].target_iqn == 'iqn.2003-01.org.linux-iscsi:target2'

    # Test failed session retrieval
    with patch('sts.iscsi.session.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not IscsiSession.get_all()


def test_session_get_by_target(mock_command_result: Any) -> None:
    """Test getting session by target.

    Args:
        mock_command_result: Mock command result fixture
    """
    # Test successful session retrieval
    with patch('sts.iscsi.session.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.session.return_value = mock_command_result(
            rc=0,
            stdout='tcp: [1] 192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target1\ntcp: [2] 192.168.1.101:3260,1 iqn.2003-01.org.linux-iscsi:target2\n',
            stderr='',
            command='',
        )
        session = IscsiSession.get_by_target('iqn.2003-01.org.linux-iscsi:target1')[0]
        assert session is not None
        assert session.session_id == '1'
        assert session.portal == '192.168.1.100:3260'
        assert session.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'

        # Test non-existent target
        assert IscsiSession.get_by_target('iqn.2003-01.org.linux-iscsi:nonexistent') == []

    # Test failed session retrieval
    with patch('sts.iscsi.session.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert IscsiSession.get_by_target('iqn.2003-01.org.linux-iscsi:target1') == []


def test_session_get_by_portal(mock_command_result: Any) -> None:
    """Test getting session by portal.

    Args:
        mock_command_result: Mock command result fixture
    """
    # Test successful session retrieval
    with patch('sts.iscsi.session.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.session.return_value = mock_command_result(
            rc=0,
            stdout='tcp: [1] 192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target1\ntcp: [2] 192.168.1.101:3260,1 iqn.2003-01.org.linux-iscsi:target2\n',
            stderr='',
            command='',
        )
        session = IscsiSession.get_by_portal('192.168.1.100:3260')[0]
        assert session is not None
        assert session.session_id == '1'
        assert session.portal == '192.168.1.100:3260'
        assert session.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'

        # Test non-existent portal
        assert IscsiSession.get_by_portal('192.168.1.102:3260') == []

    # Test failed session retrieval
    with patch('sts.iscsi.session.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert IscsiSession.get_by_portal('192.168.1.100:3260') == []


def test_session_get_parameters(mock_session: IscsiSession, mock_command_result: Any) -> None:
    """Test getting session parameters.

    Args:
        mock_session: Mock session instance
        mock_command_result: Mock command result fixture
    """
    # Test successful parameter retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(
            rc=0,
            stdout='HeaderDigest: None\nMaxRecvDataSegmentLength: 262144\n',
            stderr='',
            command='',
        )
        params = mock_session.get_parameters()
        assert params == {
            'HeaderDigest': 'None',
            'MaxRecvDataSegmentLength': '262144',
        }

    # Test failed parameter retrieval
    with patch.object(mock_session, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.session.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_session.get_parameters()
