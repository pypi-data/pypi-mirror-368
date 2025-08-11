# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test iSCSI functionality."""

from unittest.mock import MagicMock, patch

from sts.iscsi.iscsiadm import IscsiAdm


class TestIscsiAdm:
    """Test IscsiAdm class."""

    @patch('sts.utils.system.SystemManager')
    def test_init(self, mock_system: MagicMock) -> None:
        """Test initialization."""
        # Mock package manager
        mock_system.return_value.package_manager.install.return_value = True
        admin = IscsiAdm()
        assert admin.debug_level == 0

    def test_get_short_options_list(self) -> None:
        """Test getting short options list."""
        with patch('sts.utils.system.SystemManager') as mock_system:
            mock_system.return_value.package_manager.install.return_value = True
            admin = IscsiAdm()
            assert admin.get_short_options_list('discovery') == list('DSIPdntplov')

    def test_get_long_options_list(self) -> None:
        """Test getting long options list."""
        with patch('sts.utils.system.SystemManager') as mock_system:
            mock_system.return_value.package_manager.install.return_value = True
            admin = IscsiAdm()
            long_opts = admin.get_long_options_list('discovery')
            assert 'portal' in long_opts
            assert 'discover' in long_opts

    def test_available_options(self) -> None:
        """Test getting all available options."""
        with patch('sts.utils.system.SystemManager') as mock_system:
            mock_system.return_value.package_manager.install.return_value = True
            admin = IscsiAdm()
            opts = admin.available_options('discovery')
            assert 'p' in opts
            assert 'portal' in opts

    def test_discovery(self) -> None:
        """Test discovery command."""
        with patch('sts.utils.system.SystemManager') as mock_system:
            mock_system.return_value.package_manager.install.return_value = True
            with patch('sts.iscsi.iscsiadm.run') as mock_run:
                # Mock command result
                mock_result = MagicMock()
                mock_result.succeeded = True
                mock_run.return_value = mock_result

                admin = IscsiAdm()

                # Test basic discovery
                admin.discovery()
                mock_run.assert_called_with('iscsiadm --mode discovery -t st -p 127.0.0.1')

                # Test with interface
                mock_run.reset_mock()
                mock_run.return_value = mock_result
                admin.discovery(interface='eth0')
                mock_run.assert_called_with('iscsiadm --mode discovery -t st -p 127.0.0.1 -I eth0')

    def test_node_operations(self) -> None:
        """Test node operations."""
        with patch('sts.utils.system.SystemManager') as mock_system:
            mock_system.return_value.package_manager.install.return_value = True
            with patch('sts.iscsi.iscsiadm.run') as mock_run:
                # Mock command result
                mock_result = MagicMock()
                mock_result.succeeded = True
                mock_run.return_value = mock_result

                admin = IscsiAdm()

                # Test login
                admin.node_login()
                mock_run.assert_called_with('iscsiadm --mode node --login')

                # Test logout
                mock_run.reset_mock()
                mock_run.return_value = mock_result
                admin.node_logout()
                mock_run.assert_called_with('iscsiadm --mode node --logout')

                # Test logoutall
                mock_run.reset_mock()
                mock_run.return_value = mock_result
                admin.node_logoutall()
                mock_run.assert_called_with('iscsiadm --mode node --logoutall all')

    def test_iface_operations(self) -> None:
        """Test interface operations."""
        with patch('sts.utils.system.SystemManager') as mock_system:
            mock_system.return_value.package_manager.install.return_value = True
            with patch('sts.iscsi.iscsiadm.run') as mock_run:
                # Mock command result
                mock_result = MagicMock()
                mock_result.succeeded = True
                mock_run.return_value = mock_result

                admin = IscsiAdm()

                # Test update
                admin.iface_update('eth0', 'initiatorname', 'iqn.test')
                mock_run.assert_called_with(
                    'iscsiadm --mode iface -o update -I eth0 -n iface.initiatorname -v iqn.test'
                )

                # Test exists
                mock_run.reset_mock()
                mock_run.return_value = mock_result
                assert admin.iface_exists('eth0') is True
                mock_run.assert_called_with('iscsiadm --mode iface -o show -I eth0')
