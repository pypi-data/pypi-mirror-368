# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test system operations module."""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

from sts.utils.system import SystemInfo, SystemManager


class TestSystemInfo:
    """Test SystemInfo class."""

    def test_init_defaults(self) -> None:
        """Test default initialization."""
        info = SystemInfo()
        assert info._hostname is None
        assert info._kernel is None
        assert info._arch is None
        assert info._distribution is None
        assert info._release is None
        assert info._codename is None

    @patch('sts.utils.system.run')
    def test_hostname(self, mock_run: MagicMock) -> None:
        """Test hostname property."""
        info = SystemInfo()

        # Test successful hostname
        mock_result = MagicMock()
        mock_result.succeeded = True
        mock_result.stdout = 'test-host\n'
        mock_run.return_value = mock_result
        assert info.hostname == 'test-host'
        assert info._hostname == 'test-host'  # Cached

        # Test failed hostname
        info = SystemInfo()
        mock_result.succeeded = False
        assert info.hostname is None
        assert info._hostname is None

    @patch('sts.utils.system.host')
    def test_kernel(self, mock_host: MagicMock) -> None:
        """Test kernel property."""
        info = SystemInfo()
        mock_host.sysctl.return_value = '5.4.0-1.el8'
        assert info.kernel == '5.4.0-1.el8'
        assert info._kernel == '5.4.0-1.el8'  # Cached

    @patch('sts.utils.system.host')
    def test_arch(self, mock_host: MagicMock) -> None:
        """Test arch property."""
        info = SystemInfo()
        mock_host.system_info.arch = 'x86_64'
        assert info.arch == 'x86_64'
        assert info._arch == 'x86_64'  # Cached

    @patch('sts.utils.system.host')
    def test_distribution(self, mock_host: MagicMock) -> None:
        """Test distribution property."""
        info = SystemInfo()
        mock_host.system_info.distribution = 'fedora'
        assert info.distribution == 'fedora'
        assert info._distribution == 'fedora'  # Cached

    @patch('sts.utils.system.host')
    def test_release(self, mock_host: MagicMock) -> None:
        """Test release property."""
        info = SystemInfo()
        mock_host.system_info.release = '38'
        assert info.release == '38'
        assert info._release == '38'  # Cached

    @patch('sts.utils.system.host')
    def test_codename(self, mock_host: MagicMock) -> None:
        """Test codename property."""
        info = SystemInfo()
        mock_host.system_info.codename = 'thirty eight'
        assert info.codename == 'thirty eight'
        assert info._codename == 'thirty eight'  # Cached

    def test_get_current(self) -> None:
        """Test get_current method."""
        info = SystemInfo.get_current()
        assert isinstance(info, SystemInfo)

    def test_is_debug(self) -> None:
        """Test is_debug property."""
        info = SystemInfo()
        with patch.object(SystemInfo, 'kernel', new_callable=PropertyMock) as mock_kernel:
            mock_kernel.return_value = '5.4.0-1.el8+debug'
            assert info.is_debug is True
            mock_kernel.return_value = '5.4.0-1.el8'
            assert info.is_debug is False

    @patch('pathlib.Path.read_text')
    def test_in_container(self, mock_read: MagicMock) -> None:
        """Test in_container property."""
        info = SystemInfo()

        # Test container_t
        mock_read.side_effect = ['container_t', '']
        assert info.in_container is True

        # Test unconfined
        mock_read.side_effect = ['unconfined', '']
        assert info.in_container is True

        # Test docker
        mock_read.side_effect = ['', 'docker']
        assert info.in_container is True

        # Test not in container
        mock_read.side_effect = ['', '']
        assert info.in_container is False

        # Test permission error
        mock_read.side_effect = PermissionError()
        assert info.in_container is True

    def test_log_all(self) -> None:
        """Test log_all method."""
        info = SystemInfo()
        with patch('logging.info') as mock_log:
            info.log_all()
            assert (
                mock_log.call_count in (7, 8)
            )  # hostname, kernel, arch, distribution, release, codename, in_container, plus one possible log when running 'uname -r'


class TestSystemManager:
    """Test SystemManager class."""

    def test_init(self) -> None:
        """Test initialization."""
        sm = SystemManager()
        assert isinstance(sm.info, SystemInfo)
        assert sm.package_manager is not None

    def test_get_timestamp(self) -> None:
        """Test get_timestamp method."""
        sm = SystemManager()
        timestamp = sm.get_timestamp()
        assert len(timestamp) == 14  # YYYYMMDDhhmmss
        assert timestamp.isdigit()

        timestamp = sm.get_timestamp('utc')
        assert len(timestamp) == 14
        assert timestamp.isdigit()

    @patch('sts.utils.system.run')
    def test_clear_logs(self, mock_run: MagicMock) -> None:
        """Test clear_logs method."""
        sm = SystemManager()
        sm.clear_logs()
        mock_run.assert_called_with('dmesg -c')

    @patch('sts.utils.system.run')
    def test_service_operations(self, mock_run: MagicMock) -> None:
        """Test service operations."""
        sm = SystemManager()
        mock_result = MagicMock()
        mock_result.succeeded = True
        mock_run.return_value = mock_result

        # Test is_service_enabled
        assert sm.is_service_enabled('sshd') is True
        mock_run.assert_called_with('systemctl is-enabled sshd')

        # Test is_service_running
        assert sm.is_service_running('sshd') is True
        mock_run.assert_called_with('systemctl is-active sshd')

        # Test service_enable
        assert sm.service_enable('sshd') is True
        mock_run.assert_called_with('systemctl enable sshd')

        # Test service_disable
        assert sm.service_disable('sshd') is True
        mock_run.assert_called_with('systemctl disable sshd')

        # Test service_start
        assert sm.service_start('sshd') is True
        mock_run.assert_called_with('systemctl start sshd')

        # Test service_stop
        assert sm.service_stop('sshd') is True
        mock_run.assert_called_with('systemctl stop sshd')

        # Test service_restart
        assert sm.service_restart('sshd') is True
        mock_run.assert_called_with('systemctl restart sshd')

    @patch('sts.utils.system.SystemManager.is_service_enabled')
    @patch('sts.utils.system.SystemManager.service_enable')
    @patch('sts.utils.system.SystemManager.service_disable')
    @patch('time.sleep')
    def test_test_service_enable_cycle(
        self,
        mock_sleep: MagicMock,
        mock_disable: MagicMock,
        mock_enable: MagicMock,
        mock_is_enabled: MagicMock,
    ) -> None:
        """Test _test_service_enable_cycle method."""
        sm = SystemManager()

        # Test disable -> enable cycle
        mock_is_enabled.return_value = True
        mock_disable.return_value = True
        mock_enable.return_value = True
        assert sm._test_service_enable_cycle('sshd') is True

        # Test enable -> disable cycle
        mock_is_enabled.return_value = False
        mock_enable.return_value = True
        mock_disable.return_value = True
        assert sm._test_service_enable_cycle('sshd') is True

        # Test failure
        mock_disable.return_value = False
        assert sm._test_service_enable_cycle('sshd') is False

        # Verify sleep was mocked
        mock_sleep.assert_called()

    @patch('sts.utils.system.SystemManager.is_service_running')
    @patch('sts.utils.system.SystemManager.service_start')
    @patch('sts.utils.system.SystemManager.service_stop')
    @patch('time.sleep')
    def test_test_service_start_cycle(
        self,
        mock_sleep: MagicMock,
        mock_stop: MagicMock,
        mock_start: MagicMock,
        mock_is_running: MagicMock,
    ) -> None:
        """Test _test_service_start_cycle method."""
        sm = SystemManager()

        # Test stop -> start cycle
        mock_is_running.return_value = True
        mock_stop.return_value = True
        mock_start.return_value = True
        assert sm._test_service_start_cycle('sshd') is True

        # Test start -> stop cycle
        mock_is_running.return_value = False
        mock_start.return_value = True
        mock_stop.return_value = True
        assert sm._test_service_start_cycle('sshd') is True

        # Test failure
        mock_stop.return_value = False
        assert sm._test_service_start_cycle('sshd') is False

        # Verify sleep was mocked
        mock_sleep.assert_called()

    @patch('sts.utils.system.SystemManager.service_restart')
    @patch('sts.utils.system.SystemManager.is_service_running')
    @patch('time.sleep')
    def test_test_service_restart(
        self,
        mock_sleep: MagicMock,
        mock_is_running: MagicMock,
        mock_restart: MagicMock,
    ) -> None:
        """Test _test_service_restart method."""
        sm = SystemManager()

        # Test successful restart
        mock_restart.return_value = True
        mock_is_running.return_value = True
        assert sm._test_service_restart('sshd') is True

        # Test failed restart
        mock_restart.return_value = False
        assert sm._test_service_restart('sshd') is False

        # Verify sleep was mocked
        mock_sleep.assert_called()

    @patch('sts.utils.system.SystemManager._test_service_enable_cycle')
    @patch('sts.utils.system.SystemManager._test_service_start_cycle')
    @patch('sts.utils.system.SystemManager._test_service_restart')
    def test_test_service(
        self,
        mock_restart: MagicMock,
        mock_start: MagicMock,
        mock_enable: MagicMock,
    ) -> None:
        """Test test_service method."""
        sm = SystemManager()

        # Test all operations succeed
        mock_enable.return_value = True
        mock_start.return_value = True
        mock_restart.return_value = True
        assert sm.test_service('sshd') is True

        # Test enable cycle fails
        mock_enable.return_value = False
        assert sm.test_service('sshd') is False

        # Test start cycle fails
        mock_enable.return_value = True
        mock_start.return_value = False
        assert sm.test_service('sshd') is False

        # Test restart fails
        mock_start.return_value = True
        mock_restart.return_value = False
        assert sm.test_service('sshd') is False
