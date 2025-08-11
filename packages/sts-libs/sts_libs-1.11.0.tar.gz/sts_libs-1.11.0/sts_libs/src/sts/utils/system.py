# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""System utilities.

This module provides functionality for system operations:
- System information
- System logs
- System state
- Service management
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Final, Literal

from sts import get_sts_host
from sts.utils.cmdline import run
from sts.utils.packages import Dnf, ensure_installed
from sts.utils.version import VersionInfo

host = get_sts_host()

# Constants
MIN_LOG_PARTS: Final[int] = 4  # Minimum parts in a log line (timestamp, host, service, message)
SERVICE_WAIT_TIME: Final[int] = 5  # Seconds to wait after service operations


class LogFormat(Enum):
    """Log format options."""

    DEFAULT = auto()
    KERNEL = auto()
    REVERSE = auto()


@dataclass
class LogOptions:
    """Log retrieval options.

    This class provides options for log retrieval:
    - Format options
    - Filtering options
    - Time range options

    Args:
        format: Log format (optional, defaults to DEFAULT)
        length: Number of lines (optional)
        since: Since timestamp (optional)
        grep: Filter pattern (optional)
        options: Additional options (optional)

    Example:
        ```python
        opts = LogOptions()  # Uses defaults
        opts = LogOptions(format=LogFormat.KERNEL)  # Custom format
        ```
    """

    # Optional parameters with defaults
    format: LogFormat = LogFormat.DEFAULT

    # Optional parameters without defaults
    length: int | None = None
    since: str | None = None
    grep: str | None = None
    options: list[str] = field(default_factory=list)


@dataclass
class SystemInfo:
    """System information.

    This class provides functionality for system information:
    - Operating system details
    - Hardware information
    - System state

    Properties:
        hostname: System hostname
        kernel: Kernel version
        arch: System architecture
        distribution: Distribution name
        release: Distribution release
        codename: Distribution codename

    Example:
        ```python
        info = SystemInfo()  # Discovers values when needed
        print(info.hostname)  # Discovers hostname on first access
        'localhost'
        ```
    """

    # Optional parameters
    _hostname: str | None = field(default=None, init=False)
    _kernel: str | None = field(default=None, init=False)
    _arch: str | None = field(default=None, init=False)
    _distribution: str | None = field(default=None, init=False)
    _release: str | None = field(default=None, init=False)
    _codename: str | None = field(default=None, init=False)

    @property
    def hostname(self) -> str | None:
        """Get system hostname.

        Returns:
            System hostname or None if not found

        Example:
            ```python
            info.hostname
            'localhost'
            ```
        """
        if self._hostname is None:
            result = run('hostname')
            if result.succeeded:
                self._hostname = result.stdout.strip()
        return self._hostname

    @property
    def kernel(self) -> str | None:
        """Get kernel version.

        Returns:
            Kernel version or None if not found

        Example:
            ```python
            info.kernel
            '5.4.0-1.el8'
            ```
        """
        if self._kernel is None:
            try:
                self._kernel = host.sysctl('kernel.osrelease')  # type: ignore[assignment]
            except ValueError:  # sysctl not available
                self._kernel = run('uname -r').stdout.strip()

        return self._kernel

    @property
    def arch(self) -> str | None:
        """Get system architecture.

        Returns:
            System architecture or None if not found

        Example:
            ```python
            info.arch
            'x86_64'
            ```
        """
        if self._arch is None:
            self._arch = host.system_info.arch  # type: ignore[assignment]
        return self._arch

    @property
    def distribution(self) -> str | None:
        """Get distribution name.

        Returns:
            Distribution name or None if not found

        Example:
            ```python
            info.distribution
            'fedora'
            ```
        """
        if self._distribution is None:
            self._distribution = host.system_info.distribution  # type: ignore[assignment]
        return self._distribution

    @property
    def release(self) -> str | None:
        """Get distribution release.

        Returns:
            Distribution release or None if not found

        Example:
            ```python
            info.release
            '38'
            ```
        """
        if self._release is None:
            self._release = host.system_info.release  # type: ignore[assignment]
        return self._release

    @property
    def version(self) -> VersionInfo:
        """Get distribution release as a VersionInfo.

        Returns:
            VersionInfo: A named tuple representing the distribution release with major, minor, and micro components.

        Example:
            ```python
            info.version
            VersionInfo(major='8', minor='10', micro='1')
            ```
        """
        if self.release:
            return VersionInfo.from_string(self.release)
        return VersionInfo(major=0)

    @property
    def codename(self) -> str | None:
        """Get distribution codename.

        Returns:
            Distribution codename or None if not found

        Example:
            ```python
            info.codename
            'thirty eight'
            ```
        """
        if self._codename is None:
            self._codename = host.system_info.codename  # type: ignore[assignment]
        return self._codename

    @classmethod
    def get_current(cls) -> SystemInfo:
        """Get current system information.

        Returns:
            System information

        Example:
            ```python
            info = SystemInfo.get_current()
            info.kernel
            '5.4.0-1.el8'
            ```
        """
        return cls()  # Values will be discovered when needed

    @property
    def is_debug(self) -> bool:
        """Check if running debug kernel.

        Returns:
            True if debug kernel, False otherwise

        Example:
            ```python
            info.is_debug
            False
            ```
        """
        return bool(self.kernel and '+debug' in self.kernel)

    @property
    def in_container(self) -> bool:
        """Check if running in container.

        Returns:
            True if in container, False otherwise

        Example:
            ```python
            info.in_container
            False
            ```
        """
        try:
            proc_current = Path('/proc/1/attr/current').read_text()
            if 'container_t' in proc_current or 'unconfined' in proc_current:
                return True
            if 'docker' in Path('/proc/self/cgroup').read_text():
                return True
        except PermissionError:
            logging.info('Assuming containerized environment')
            return True
        return False

    def log_all(self) -> None:
        """Log all system information.

        Example:
            ```python
            info = SystemInfo()
            info.log_all()
            INFO: Hostname: localhost
            INFO: Kernel: 5.4.0-1.el8
            INFO: Architecture: x86_64
            INFO: Distribution: fedora
            INFO: Release: 38
            INFO: Codename: thirty eight
            ```
        """
        logging.info(f'Hostname: {self.hostname}')
        logging.info(f'Kernel: {self.kernel}')
        logging.info(f'Architecture: {self.arch}')
        logging.info(f'Distribution: {self.distribution}')
        logging.info(f'Release: {self.release}')
        logging.info(f'Codename: {self.codename}')


class SystemManager:
    """System manager functionality.

    This class provides functionality for system operations:
    - System information
    - System logs
    - System state
    - Service management

    Example:
        ```python
        sm = SystemManager()
        sm.get_logs(LogOptions(format=LogFormat.KERNEL))
        'Jan 1 00:00:00 kernel: ...'
        ```
    """

    def __init__(self) -> None:
        """Initialize system manager."""
        self.info = SystemInfo.get_current()
        self.package_manager = Dnf()

    def get_logs(self, options: LogOptions | None = None) -> str | None:
        """Get system logs.

        Args:
            options: Log options

        Returns:
            Log output or None if error

        Example:
            ```python
            sm = SystemManager()
            sm.get_logs(LogOptions(format=LogFormat.KERNEL))
            'Jan 1 00:00:00 kernel: ...'
            ```
        """
        options = options or LogOptions()

        # Build command
        cmd = ['journalctl']
        if options.format == LogFormat.KERNEL:
            cmd.append('-k')
        if options.length:
            cmd.extend(['-n', str(options.length)])
        if options.format == LogFormat.REVERSE:
            cmd.append('-r')
        if options.since:
            cmd.extend(['-S', options.since])
        if options.options:
            cmd.extend(options.options)
        if options.grep:
            cmd.extend(['|', 'grep', f"'{options.grep}'"])

        result = run(' '.join(cmd))
        if result.failed:
            logging.error('Failed to get system logs')
            return None

        # Format output to match /var/log/messages
        output = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < MIN_LOG_PARTS:
                continue
            parts[3] = parts[3].split('.')[0]
            output.append(' '.join(parts))

        return '\n'.join(output)

    def generate_sosreport(self, skip_plugins: str | None = None, plugin_timeout: int = 300) -> str | None:
        """Generate sosreport.

        Args:
            skip_plugins: Plugins to skip
            plugin_timeout: Plugin timeout in seconds

        Returns:
            Path to sosreport or None if error

        Example:
            ```python
            sm = SystemManager()
            sm.generate_sosreport(skip_plugins='kdump,networking')
            '/tmp/sosreport-localhost-123456-2021-01-01-abcdef.tar.xz'
            ```
        """
        ensure_installed('sos')

        cmd = ['sos', 'report', '--batch', f'--plugin-timeout={plugin_timeout}']
        if skip_plugins:
            cmd.extend(['--skip-plugins', skip_plugins])

        result = run(' '.join(cmd))
        if result.failed:
            logging.error('Failed to generate sosreport')
            return None

        # Find sosreport path in output
        for line in result.stdout.splitlines():
            if '/tmp/sosreport' in line:
                return line.strip()

        return None

    def get_timestamp(self, timezone_: Literal['utc', 'local'] = 'local') -> str:
        """Get current timestamp.

        Args:
            timezone_: Timezone to use

        Returns:
            Timestamp string (YYYYMMDDhhmmss)

        Example:
            ```python
            sm = SystemManager()
            sm.get_timestamp()
            '20210101000000'
            ```
        """
        return datetime.now(tz=timezone.utc if timezone_ == 'utc' else None).strftime('%Y%m%d%H%M%S')

    def clear_logs(self) -> None:
        """Clear system logs.

        Example:
            ```python
            sm = SystemManager()
            sm.clear_logs()
            ```
        """
        run('dmesg -c')

    def is_service_enabled(self, service: str) -> bool:
        """Check if service is enabled.

        Args:
            service: Service name

        Returns:
            True if service is enabled, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.is_service_enabled('sshd')
            True
            ```
        """
        result = run(f'systemctl is-enabled {service}')
        return result.succeeded

    def is_service_running(self, service: str) -> bool:
        """Check if service is running.

        Args:
            service: Service name

        Returns:
            True if service is running, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.is_service_running('sshd')
            True
            ```
        """
        result = run(f'systemctl is-active {service}')
        return result.succeeded

    def service_enable(self, service: str) -> bool:
        """Enable service.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.service_enable('sshd')
            True
            ```
        """
        result = run(f'systemctl enable {service}')
        return result.succeeded

    def service_disable(self, service: str) -> bool:
        """Disable service.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.service_disable('sshd')
            True
            ```
        """
        result = run(f'systemctl disable {service}')
        return result.succeeded

    def service_start(self, service: str) -> bool:
        """Start service.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.service_start('sshd')
            True
            ```
        """
        result = run(f'systemctl start {service}')
        return result.succeeded

    def service_stop(self, service: str) -> bool:
        """Stop service.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.service_stop('sshd')
            True
            ```
        """
        result = run(f'systemctl stop {service}')
        return result.succeeded

    def service_restart(self, service: str) -> bool:
        """Restart service.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.service_restart('sshd')
            True
            ```
        """
        result = run(f'systemctl restart {service}')
        return result.succeeded

    def _test_service_enable_cycle(self, service: str) -> bool:
        """Test service enable/disable cycle.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise
        """
        if self.is_service_enabled(service):
            # Test disable -> enable
            if not self.service_disable(service):
                return False
            time.sleep(SERVICE_WAIT_TIME)
            return self.service_enable(service)
        # Test enable -> disable
        if not self.service_enable(service):
            return False
        time.sleep(SERVICE_WAIT_TIME)
        return self.service_disable(service)

    def _test_service_start_cycle(self, service: str) -> bool:
        """Test service start/stop cycle.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise
        """
        if self.is_service_running(service):
            # Test stop -> start
            if not self.service_stop(service):
                return False
            time.sleep(SERVICE_WAIT_TIME)
            return self.service_start(service)
        # Test start -> stop
        if not self.service_start(service):
            return False
        time.sleep(SERVICE_WAIT_TIME)
        return self.service_stop(service)

    def _test_service_restart(self, service: str) -> bool:
        """Test service restart.

        Args:
            service: Service name

        Returns:
            True if successful, False otherwise
        """
        if not self.service_restart(service):
            return False
        time.sleep(SERVICE_WAIT_TIME)
        return self.is_service_running(service)

    def test_service(self, service: str) -> bool:
        """Test service operations.

        This method tests:
        - Enable/disable cycle
        - Start/stop cycle
        - Restart operation

        Args:
            service: Service name

        Returns:
            True if all tests pass, False otherwise

        Example:
            ```python
            sm = SystemManager()
            sm.test_service('sshd')
            True
            ```
        """
        # Test enable/disable cycle
        if not self._test_service_enable_cycle(service):
            return False

        # Test start/stop cycle
        if not self._test_service_start_cycle(service):
            return False

        # Test restart
        return self._test_service_restart(service)
