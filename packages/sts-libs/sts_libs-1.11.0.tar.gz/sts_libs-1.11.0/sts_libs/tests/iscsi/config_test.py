# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test iSCSI configuration management.

This module tests:
- Interface configuration
- Node configuration
- Overall configuration
- Daemon configuration
"""

import os
from pathlib import Path
from typing import Any
from unittest.mock import call, patch

import pytest

from sts.iscsi.config import (
    IscsiConfig,
    IscsidConfig,
    IscsiInterface,
    IscsiNode,
    create_iscsi_iface,
    rand_iscsi_string,
    set_initiatorname,
    setup,
)

# pytest is used for the tmp_path fixture
pytest_mark = pytest.mark

# Check if we're running as root
IS_ROOT = os.geteuid() == 0


def test_rand_iscsi_string() -> None:
    """Test random iSCSI string generation."""
    # Test valid length
    result = rand_iscsi_string(8)
    assert result is not None
    assert len(result) == 8
    assert all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],~' for c in result)

    # Test invalid length
    result = rand_iscsi_string(0)
    assert result == ''  # Function returns empty string, not None

    result = rand_iscsi_string(-1)
    assert result == ''  # Function returns empty string, not None


def test_set_initiatorname(tmp_path: Path) -> None:
    """Test setting initiator name.

    Args:
        tmp_path: Temporary directory
    """
    config_file = tmp_path / 'initiatorname.iscsi'
    with patch('sts.iscsi.config.Path') as mock_path:
        mock_path.return_value = config_file
        assert set_initiatorname('iqn.2003-01.org.linux-iscsi:initiator1')
        assert config_file.read_text() == 'InitiatorName=iqn.2003-01.org.linux-iscsi:initiator1\n'

        # Test write failure
        mock_path.return_value = Path('/nonexistent/path')
        assert not set_initiatorname('iqn.2003-01.org.linux-iscsi:initiator1')


def test_create_iscsi_iface(mock_command_result: Any) -> None:
    """Test creating iSCSI interface.

    Args:
        mock_command_result: Mock command result fixture
    """
    with patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm:
        # Test successful creation
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        assert create_iscsi_iface('iface0')
        mock_iscsiadm.return_value.iface.assert_called_once_with(op='new', iface='iface0')

        # Test failed creation
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=1, stdout='', stderr='error', command='')
        assert not create_iscsi_iface('iface1')


def test_iscsi_interface() -> None:
    """Test IscsiInterface class."""
    # Test basic interface
    iface = IscsiInterface(iscsi_ifacename='iface0', ipaddress='127.0.0.1')
    assert iface.iscsi_ifacename == 'iface0'
    assert iface.ipaddress == '127.0.0.1'
    assert iface.hwaddress is None

    # Test interface with hardware address
    iface = IscsiInterface(iscsi_ifacename='iface0', ipaddress='127.0.0.1', hwaddress='00:11:22:33:44:55')
    assert iface.iscsi_ifacename == 'iface0'
    assert iface.ipaddress == '127.0.0.1'
    assert iface.hwaddress == '00:11:22:33:44:55'

    # Test interface with qedi/bnx2i
    iface = IscsiInterface(iscsi_ifacename='qedi0', ipaddress='127.0.0.1')
    assert iface.iscsi_ifacename == 'qedi0'
    assert iface.ipaddress == '127.0.0.1'

    iface = IscsiInterface(iscsi_ifacename='bnx2i0', ipaddress='127.0.0.1')
    assert iface.iscsi_ifacename == 'bnx2i0'
    assert iface.ipaddress == '127.0.0.1'


@pytest.mark.skip(reason='TODO: Fix test to properly mock iscsiadm discovery and login sequence')
def test_iscsi_node(mock_command_result: Any) -> None:
    """Test IscsiNode class.

    Args:
        mock_command_result: Mock command result fixture
    """
    # Test basic node
    node = IscsiNode(target_iqn='iqn.2003-01.org.linux-iscsi:target1', portal='127.0.0.1:3260', interface='iface0')
    assert node.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'
    assert node.portal == '127.0.0.1:3260'
    assert node.interface == 'iface0'

    # Test login/logout
    with patch.object(node, '_iscsiadm') as mock_iscsiadm:
        mock_iscsiadm.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.node_login.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.node_logout.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')

        assert node.login()
        mock_iscsiadm.discovery.assert_called_once_with(portal='127.0.0.1:3260')
        mock_iscsiadm.node_login.assert_called_once()

        assert node.logout()
        mock_iscsiadm.node_logout.assert_called_once()

    # Test setup_and_login
    with patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm:
        # Mock discovery to return a target
        discovery_result = mock_command_result(
            rc=0,
            stdout='192.168.1.100:3260,1 iqn.2003-01.org.linux-iscsi:target1',
            stderr='',
            command='',
        )
        mock_iscsiadm.return_value.discovery.side_effect = [
            discovery_result,  # First call during discovery
            discovery_result,  # Second call during login
        ]
        mock_iscsiadm.return_value.node_login.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')

        # Test with target IQN
        node = IscsiNode.setup_and_login(
            portal='192.168.1.100:3260',
            initiator_iqn='iqn.2003-01.org.linux-iscsi:initiator1',
            target_iqn='iqn.2003-01.org.linux-iscsi:target1',
        )
        assert node.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'
        assert node.portal == '192.168.1.100:3260'

        # Test without target IQN (discover)
        node = IscsiNode.setup_and_login(
            portal='192.168.1.100:3260', initiator_iqn='iqn.2003-01.org.linux-iscsi:initiator1'
        )
        assert node.target_iqn == 'iqn.2003-01.org.linux-iscsi:target1'
        assert node.portal == '192.168.1.100:3260'


def test_iscsi_config() -> None:
    """Test IscsiConfig class."""
    # Test basic config
    config = IscsiConfig(
        initiatorname='iqn.2003-01.org.linux-iscsi:initiator1',
        ifaces=[IscsiInterface(iscsi_ifacename='iface0', ipaddress='127.0.0.1')],
        targets=[
            IscsiNode(target_iqn='iqn.2003-01.org.linux-iscsi:target1', portal='127.0.0.1:3260', interface='iface0')
        ],
        driver='iscsi_tcp',
    )

    # Test with qedi/bnx2i interfaces
    config = IscsiConfig(
        initiatorname='iqn.2003-01.org.linux-iscsi:initiator1',
        ifaces=[
            IscsiInterface(iscsi_ifacename='qedi0', ipaddress='127.0.0.1'),
            IscsiInterface(iscsi_ifacename='bnx2i0', ipaddress='127.0.0.1'),
        ],
        targets=[],
        driver='iscsi_tcp',
    )
    assert len(config.ifaces) == 2
    assert config.ifaces[0].iscsi_ifacename == 'qedi0'
    assert config.ifaces[1].iscsi_ifacename == 'bnx2i0'


@pytest.mark.skipif(not IS_ROOT, reason='Requires root privileges to modify iscsid.conf')
def test_iscsid_config(tmp_path: Path) -> None:
    """Test IscsidConfig class.

    Args:
        tmp_path: Temporary directory
    """
    config_file = tmp_path / 'iscsid.conf'
    config_file.write_text("""# iSCSI daemon config
iscsid.startup = /bin/systemctl start iscsid.socket iscsiuio.socket

# Node settings
node.startup = automatic
node.leading_login = No

# CHAP settings
node.session.auth.authmethod = CHAP
node.session.auth.username = user
node.session.auth.password = pass""")

    with patch.object(IscsidConfig, 'CONFIG_PATH', config_file):
        # Test loading config
        config = IscsidConfig()
        assert config.get_parameter('iscsid.startup') == '/bin/systemctl start iscsid.socket iscsiuio.socket'
        assert config.get_parameter('node.startup') == 'automatic'
        assert config.get_parameter('node.session.auth.authmethod') == 'CHAP'

        # Test setting parameters
        config.set_parameters({'node.startup': 'manual'})
        assert config.get_parameter('node.startup') == 'manual'

        # Test saving config
        assert config.save()
        new_config = IscsidConfig()
        assert new_config.get_parameter('node.startup') == 'manual'

        # Test loading non-existent config
        with patch.object(IscsidConfig, 'CONFIG_PATH', Path('/nonexistent')):
            config = IscsidConfig()
            assert not config.parameters


@pytest.mark.skipif(not IS_ROOT, reason='Requires root privileges to modify iscsid.conf')
def test_setup(mock_command_result: Any) -> None:
    """Test setup functions.

    Args:
        mock_command_result: Mock command result fixture
    """
    # Test basic config (no qedi/bnx2i)
    config = IscsiConfig(
        initiatorname='iqn.2003-01.org.linux-iscsi:initiator1',
        ifaces=[IscsiInterface(iscsi_ifacename='iface0', ipaddress='127.0.0.1')],
        targets=[
            IscsiNode(target_iqn='iqn.2003-01.org.linux-iscsi:target1', portal='127.0.0.1:3260', interface='iface0')
        ],
        driver='iscsi_tcp',
    )

    # Test successful setup
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
        patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_enable.return_value = True
        mock_system.return_value.service_start.return_value = True
        mock_system.return_value.is_service_enabled.return_value = False
        mock_system.return_value.is_service_running.return_value = False
        mock_iscsiadm.return_value.iface_exists.return_value = False
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.return_value.iface_update.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=''
        )
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')

        assert setup(config)
        mock_set_initiator.assert_called_once_with('iqn.2003-01.org.linux-iscsi:initiator1')
        mock_system.return_value.service_enable.assert_called_once_with('iscsid')
        mock_iscsiadm.return_value.iface.assert_called_once()
        mock_iscsiadm.return_value.discovery.assert_called_once()

    # Test config with qedi/bnx2i
    config = IscsiConfig(
        initiatorname='iqn.2003-01.org.linux-iscsi:initiator1',
        ifaces=[
            IscsiInterface(iscsi_ifacename='qedi0', ipaddress='127.0.0.1'),
            IscsiInterface(iscsi_ifacename='bnx2i0', ipaddress='127.0.0.1'),
        ],
        targets=[
            IscsiNode(target_iqn='iqn.2003-01.org.linux-iscsi:target1', portal='127.0.0.1:3260', interface='qedi0')
        ],
        driver='qedi',  # Set driver to qedi to enable iscsiuio
    )

    # Test successful setup with qedi/bnx2i
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
        patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_enable.return_value = True
        mock_system.return_value.service_start.return_value = True
        mock_system.return_value.is_service_enabled.return_value = False
        mock_system.return_value.is_service_running.return_value = False
        mock_iscsiadm.return_value.iface_exists.return_value = False
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.return_value.iface_update.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=''
        )
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')

        assert setup(config)
        mock_set_initiator.assert_called_once_with('iqn.2003-01.org.linux-iscsi:initiator1')
        mock_iscsiadm.return_value.discovery.assert_called_once()

    # Test failed initiator setup
    with patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator:
        mock_set_initiator.return_value = False
        assert not setup(config)

    # Test failed service restart
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_restart.return_value = False
        assert not setup(config)

    # Test failed service start
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_restart.return_value = True
        mock_system.return_value.service_start.return_value = False
        assert not setup(config)

    # Test failed interface update
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
        patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_restart.return_value = True
        mock_system.return_value.service_enable.return_value = True
        mock_system.return_value.service_start.return_value = True
        mock_system.return_value.is_service_enabled.return_value = False
        mock_system.return_value.is_service_running.return_value = False
        mock_iscsiadm.return_value.iface_exists.return_value = False
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.return_value.iface_update.return_value = mock_command_result(
            rc=1, stdout='', stderr='', command=''
        )
        assert not setup(config)

    # Test failed discovery
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
        patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_restart.return_value = True
        mock_system.return_value.service_enable.return_value = True
        mock_system.return_value.service_start.return_value = True
        mock_system.return_value.is_service_enabled.return_value = False
        mock_system.return_value.is_service_running.return_value = False
        mock_iscsiadm.return_value.iface_exists.return_value = False
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.return_value.iface_update.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=''
        )
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(rc=1, stdout='', stderr='', command='')
        assert not setup(config)

    # Test setup from dict
    with (
        patch('sts.iscsi.config.set_initiatorname') as mock_set_initiator,
        patch('sts.iscsi.config.SystemManager') as mock_system,
        patch('sts.iscsi.config.IscsiAdm') as mock_iscsiadm,
    ):
        mock_set_initiator.return_value = True
        mock_system.return_value.service_restart.return_value = True
        mock_system.return_value.service_enable.return_value = True
        mock_system.return_value.service_start.return_value = True
        mock_system.return_value.is_service_enabled.return_value = False
        mock_system.return_value.is_service_running.return_value = False
        mock_iscsiadm.return_value.iface_exists.return_value = False
        mock_iscsiadm.return_value.iface.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')
        mock_iscsiadm.return_value.iface_update.return_value = mock_command_result(
            rc=0, stdout='', stderr='', command=''
        )
        mock_iscsiadm.return_value.discovery.return_value = mock_command_result(rc=0, stdout='', stderr='', command='')

        assert setup(config)
        mock_set_initiator.assert_called_once_with('iqn.2003-01.org.linux-iscsi:initiator1')
        assert mock_system.return_value.service_enable.call_args_list == [
            call('iscsiuio'),  # First qedi interface
            call('iscsiuio'),  # Second bnx2i interface
            call('iscsid'),  # Always enable iscsid
        ]
        assert mock_iscsiadm.return_value.iface.call_count == 2  # One for each interface
        mock_iscsiadm.return_value.discovery.assert_called_once()
