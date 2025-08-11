# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test iSCSI device management.

This module tests:
- Device discovery
- Device information
- Device operations
- CHAP authentication
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from sts.iscsi.device import IscsiDevice


@pytest.fixture
def mock_device() -> IscsiDevice:
    """Create mock iSCSI device.

    Returns:
        IscsiDevice instance
    """
    device = IscsiDevice(
        name='sda',
        path='/dev/sda',
        size=1000000000000,
        ip='192.168.1.100',
        target_iqn='iqn.2003-01.org.linux-iscsi:target1',
    )
    # Reset session_id before each test
    device._session_id = None
    return device


def test_device_init(mock_device: IscsiDevice) -> None:
    """Test device initialization.

    Args:
        mock_device: Mock device instance
    """
    assert mock_device.name == 'sda'
    assert mock_device.path == Path('/dev/sda')
    assert mock_device.size == 1000000000000
    assert mock_device.ip == '192.168.1.100'
    assert mock_device.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'
    assert mock_device.port == 3260
    assert mock_device.initiator_iqn is None

    # Test custom port
    device = IscsiDevice(
        name='sda',
        path='/dev/sda',
        size=1000000000000,
        ip='192.168.1.100',
        target_iqn='iqn.2003-01.org.linux-iscsi:target1',
        port=3261,
    )
    assert device.port == 3261

    # Test custom initiator IQN
    device = IscsiDevice(
        name='sda',
        path='/dev/sda',
        size=1000000000000,
        ip='192.168.1.100',
        target_iqn='iqn.2003-01.org.linux-iscsi:target1',
        initiator_iqn='iqn.2003-01.org.linux-iscsi:initiator1',
    )
    assert device.initiator_iqn == 'iqn.2003-01.org.linux-iscsi:initiator1'

    # Test path as string
    device = IscsiDevice(
        name='sda',
        path=str(Path('/dev/sda')),
        size=1000000000000,
        ip='192.168.1.100',
        target_iqn='iqn.2003-01.org.linux-iscsi:target1',
    )
    assert device.path == Path('/dev/sda')


def test_device_session_id(mock_device: IscsiDevice) -> None:
    """Test getting session ID.

    Args:
        mock_device: Mock device instance
    """
    # Test no session
    with patch('sts.iscsi.device.IscsiSession') as mock_session:
        mock_session.get_all.return_value = []
        assert mock_device.session_id is None

    # Test with matching session
    with patch('sts.iscsi.device.IscsiSession') as mock_session:
        mock_session.get_all.return_value = [
            type(
                'MockSession',
                (),
                {
                    'target_iqn': 'iqn.2003-01.org.linux-iscsi:target1',
                    'portal': '192.168.1.100:3260',
                    'session_id': '1',
                },
            ),
        ]
        assert mock_device.session_id == '1'
        # Reset session_id for next test
        mock_device._session_id = None

    # Test with different target IQN (should return None)
    with patch('sts.iscsi.device.IscsiSession') as mock_session:
        mock_session.get_all.return_value = [
            type(
                'MockSession',
                (),
                {
                    'target_iqn': 'iqn.2003-01.org.linux-iscsi:target2',  # Different target
                    'portal': '192.168.1.100:3260',
                    'session_id': '1',
                },
            ),
        ]
        assert mock_device.session_id is None

    # Test with different portal IP (should return None)
    with patch('sts.iscsi.device.IscsiSession') as mock_session:
        mock_session.get_all.return_value = [
            type(
                'MockSession',
                (),
                {
                    'target_iqn': 'iqn.2003-01.org.linux-iscsi:target1',
                    'portal': '192.168.1.101:3260',  # Different IP
                    'session_id': '1',
                },
            ),
        ]
        assert mock_device.session_id is None

    # Test with different port (should return '1' since only IP prefix is checked)
    with patch('sts.iscsi.device.IscsiSession') as mock_session:
        mock_session.get_all.return_value = [
            type(
                'MockSession',
                (),
                {
                    'target_iqn': 'iqn.2003-01.org.linux-iscsi:target1',
                    'portal': '192.168.1.100:3261',  # Different port
                    'session_id': '1',
                },
            ),
        ]
        assert mock_device.session_id == '1'


def test_device_login(mock_device: IscsiDevice, mock_command_result: Any) -> None:
    """Test device login.

    Args:
        mock_device: Mock device instance
        mock_command_result: Mock command result fixture
    """
    # Test already logged in
    with patch.object(mock_device, 'session_id', '1'):
        assert mock_device.login()

    # Test successful login
    with patch.object(mock_device, 'session_id', None), patch.object(mock_device, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.node_login.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        assert mock_device.login()
        mock_iscsiadm.discovery.assert_called_once_with(portal='192.168.1.100:3260')
        mock_iscsiadm.node_login.assert_called_once()

    # Test failed discovery
    with patch.object(mock_device, 'session_id', None), patch.object(mock_device, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.discovery.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_device.login()

    # Test failed login
    with patch.object(mock_device, 'session_id', None), patch.object(mock_device, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.node_login.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_device.login()


def test_device_logout(mock_device: IscsiDevice, mock_command_result: Any) -> None:
    """Test device logout.

    Args:
        mock_device: Mock device instance
        mock_command_result: Mock command result fixture
    """
    # Test not logged in
    with patch.object(mock_device, 'session_id', None):
        assert mock_device.logout()

    # Test successful logout
    with patch.object(mock_device, 'session_id', '1'), patch.object(mock_device, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.node_logout.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        assert mock_device.logout()
        mock_iscsiadm.node_logout.assert_called_once()
        assert mock_device.session_id is None

    # Test failed logout
    with patch.object(mock_device, 'session_id', '1'), patch.object(mock_device, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.node_logout.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not mock_device.logout()


def test_device_chap(mock_device: IscsiDevice, tmp_path: Path) -> None:
    """Test CHAP authentication.

    Args:
        mock_device: Mock device instance
        tmp_path: Temporary directory
    """
    config_file = tmp_path / 'iscsid.conf'
    config_file.write_text("""# iSCSI daemon config
node.session.auth.authmethod = None
node.session.auth.username =
node.session.auth.password = """)

    # Test successful CHAP setup
    with (
        patch.object(mock_device, 'CONFIG_PATH', tmp_path),
        patch.object(mock_device, '_restart_service') as mock_restart,
    ):
        mock_restart.return_value = True
        assert mock_device.set_chap('user', 'pass')
        mock_restart.assert_called_once()

        # Verify config file was updated
        content = config_file.read_text()
        assert 'node.session.auth.authmethod = CHAP' in content
        assert 'node.session.auth.username = user' in content
        assert 'node.session.auth.password = pass' in content
        assert 'discovery.sendtargets.auth.authmethod = CHAP' in content
        assert 'discovery.sendtargets.auth.username = user' in content
        assert 'discovery.sendtargets.auth.password = pass' in content

    # Test mutual CHAP
    with (
        patch.object(mock_device, 'CONFIG_PATH', tmp_path),
        patch.object(mock_device, '_restart_service') as mock_restart,
    ):
        mock_restart.return_value = True
        assert mock_device.set_chap('user', 'pass', 'mutual_user', 'mutual_pass')
        mock_restart.assert_called_once()

        # Verify config file was updated
        content = config_file.read_text()
        assert 'node.session.auth.username_in = mutual_user' in content
        assert 'node.session.auth.password_in = mutual_pass' in content
        assert 'discovery.sendtargets.auth.username_in = mutual_user' in content
        assert 'discovery.sendtargets.auth.password_in = mutual_pass' in content

    # Test failed service restart
    with (
        patch.object(mock_device, 'CONFIG_PATH', tmp_path),
        patch.object(mock_device, '_restart_service') as mock_restart,
    ):
        mock_restart.return_value = False
        assert not mock_device.set_chap('user', 'pass')

    # Test failed config update
    with patch.object(mock_device, 'CONFIG_PATH', Path('/nonexistent')):
        assert not mock_device.set_chap('user', 'pass')

    # Test disable CHAP
    with (
        patch.object(mock_device, 'CONFIG_PATH', tmp_path),
        patch.object(mock_device, '_restart_service') as mock_restart,
    ):
        mock_restart.return_value = True
        assert mock_device.disable_chap()
        mock_restart.assert_called_once()

        # Verify config file was updated
        content = config_file.read_text()
        assert 'node.session.auth.' not in content
        assert 'discovery.sendtargets.auth.' not in content

    # Test failed disable CHAP
    with patch.object(mock_device, 'CONFIG_PATH', Path('/nonexistent')):
        assert not mock_device.disable_chap()


def test_device_discovery(mock_command_result: Any) -> None:
    """Test device discovery.

    Args:
        mock_command_result: Mock command result fixture
    """
    # Test successful discovery
    with patch('sts.iscsi.device.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(
            rc=0,
            stdout='192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target1\n192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target2',
            stderr='',
            command='',
        )
        targets = IscsiDevice.discover('192.168.1.100')
        assert len(targets) == 2
        assert targets[0] == 'iqn.2003-01.org.linux-iscsi:target1'
        assert targets[1] == 'iqn.2003-01.org.linux-iscsi:target2'

    # Test failed discovery
    with patch('sts.iscsi.device.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not IscsiDevice.discover('192.168.1.100')

    # Test empty discovery
    with patch('sts.iscsi.device.IscsiAdm') as mock_iscsiadm:
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        assert IscsiDevice.discover('192.168.1.100') == []
