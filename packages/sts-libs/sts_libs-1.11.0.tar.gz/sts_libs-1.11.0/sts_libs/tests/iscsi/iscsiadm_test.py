# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test iSCSI admin interface.

This module tests:
- Command building
- Debug level control
"""

from typing import Any
from unittest.mock import patch

from sts.iscsi.iscsiadm import IscsiAdm


def test_command_building(mock_command_result: Any) -> None:
    """Test command building.

    Args:
        mock_command_result: Mock command result fixture
    """
    with patch('sts.iscsi.iscsiadm.run') as mock_run:
        # Test discovery command
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode discovery -t st -p 127.0.0.1'
        )
        iscsiadm = IscsiAdm()
        result = iscsiadm._run('discovery', {'-t': 'st', '-p': '127.0.0.1'})
        assert result.command == b'iscsiadm --mode discovery -t st -p 127.0.0.1'

        # Test debug level
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode node -T iqn.2003-01.org.linux-iscsi:target1 --debug 1'
        )
        iscsiadm = IscsiAdm(debug_level=1)
        result = iscsiadm._run('node', {'-T': 'iqn.2003-01.org.linux-iscsi:target1'})
        assert b'--debug 1' in result.command


def test_iface_commands(mock_command_result: Any) -> None:
    """Test interface commands.

    Args:
        mock_command_result: Mock command result fixture
    """
    with patch('sts.iscsi.iscsiadm.run') as mock_run:
        # Test iface new
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode iface -o new -I iface0'
        )
        iscsiadm = IscsiAdm()
        result = iscsiadm.iface(op='new', iface='iface0')
        assert result.command == b'iscsiadm --mode iface -o new -I iface0'

        # Test iface update
        mock_run.return_value = mock_command_result(
            rc=0,
            stdout='',
            stderr='',
            command=b'iscsiadm --mode iface -o update -I iface0 -n iface.ipaddress -v 127.0.0.1',
        )
        result = iscsiadm.iface_update(iface='iface0', name='ipaddress', value='127.0.0.1')
        assert result.command == b'iscsiadm --mode iface -o update -I iface0 -n iface.ipaddress -v 127.0.0.1'

        # Test iface update IQN
        mock_run.return_value = mock_command_result(
            rc=0,
            stdout='',
            stderr='',
            command=b'iscsiadm --mode iface -o update -I iface0 -n iface.initiatorname -v iqn.2003-01.org.linux-iscsi:initiator1',
        )
        result = iscsiadm.iface_update_iqn(iface='iface0', iqn='iqn.2003-01.org.linux-iscsi:initiator1')
        assert (
            result.command
            == b'iscsiadm --mode iface -o update -I iface0 -n iface.initiatorname -v iqn.2003-01.org.linux-iscsi:initiator1'
        )

        # Test iface update IP
        mock_run.return_value = mock_command_result(
            rc=0,
            stdout='',
            stderr='',
            command=b'iscsiadm --mode iface -o update -I iface0 -n iface.ipaddress -v 127.0.0.1',
        )
        result = iscsiadm.iface_update_ip(iface='iface0', ip='127.0.0.1')
        assert result.command == b'iscsiadm --mode iface -o update -I iface0 -n iface.ipaddress -v 127.0.0.1'


def test_discovery_commands(mock_command_result: Any) -> None:
    """Test discovery commands.

    Args:
        mock_command_result: Mock command result fixture
    """
    with patch('sts.iscsi.iscsiadm.run') as mock_run:
        # Test basic discovery
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode discovery -t st -p 127.0.0.1'
        )
        iscsiadm = IscsiAdm()
        result = iscsiadm.discovery(portal='127.0.0.1')
        assert result.command == b'iscsiadm --mode discovery -t st -p 127.0.0.1'

        # Test discovery with interface
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode discovery -t st -p 127.0.0.1 -I iface0'
        )
        result = iscsiadm.discovery(portal='127.0.0.1', interface='iface0')
        assert result.command == b'iscsiadm --mode discovery -t st -p 127.0.0.1 -I iface0'

        # Test discovery with custom type
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode discovery -t fw -p 127.0.0.1'
        )
        result = iscsiadm.discovery(portal='127.0.0.1', type='fw')
        assert result.command == b'iscsiadm --mode discovery -t fw -p 127.0.0.1'


def test_node_commands(mock_command_result: Any) -> None:
    """Test node commands.

    Args:
        mock_command_result: Mock command result fixture
    """
    with patch('sts.iscsi.iscsiadm.run') as mock_run:
        # Test node login
        mock_run.return_value = mock_command_result(
            rc=0,
            stdout='',
            stderr='',
            command=b'iscsiadm --mode node -T iqn.2003-01.org.linux-iscsi:target1 -p 127.0.0.1 --login',
        )
        iscsiadm = IscsiAdm()
        result = iscsiadm.node_login(**{'-T': 'iqn.2003-01.org.linux-iscsi:target1', '-p': '127.0.0.1'})
        assert result.command == b'iscsiadm --mode node -T iqn.2003-01.org.linux-iscsi:target1 -p 127.0.0.1 --login'

        # Test node logout
        mock_run.return_value = mock_command_result(
            rc=0,
            stdout='',
            stderr='',
            command=b'iscsiadm --mode node -T iqn.2003-01.org.linux-iscsi:target1 -p 127.0.0.1 --logout',
        )
        result = iscsiadm.node_logout(**{'-T': 'iqn.2003-01.org.linux-iscsi:target1', '-p': '127.0.0.1'})
        assert result.command == b'iscsiadm --mode node -T iqn.2003-01.org.linux-iscsi:target1 -p 127.0.0.1 --logout'

        # Test node logoutall
        mock_run.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=b'iscsiadm --mode node --logoutall manual'
        )
        result = iscsiadm.node_logoutall(how='manual')
        assert result.command == b'iscsiadm --mode node --logoutall manual'


def test_session_commands(mock_command_result: Any) -> None:
    """Test session commands.

    Args:
        mock_command_result: Mock command result fixture
    """
    with patch('sts.iscsi.iscsiadm.run') as mock_run:
        # Test basic session command
        mock_run.return_value = mock_command_result(rc=0, stdout='', stderr='', command=b'iscsiadm --mode session')
        iscsiadm = IscsiAdm()
        result = iscsiadm.session()
        assert result.command == b'iscsiadm --mode session'

        # Test session with arguments
        mock_run.return_value = mock_command_result(rc=0, stdout='', stderr='', command=b'iscsiadm --mode session -P 3')
        result = iscsiadm.session(**{'-P': '3'})
        assert result.command == b'iscsiadm --mode session -P 3'
