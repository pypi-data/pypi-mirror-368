# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Process management.

This module provides functionality for managing system processes:
- Process information
- Process control
- Process monitoring
"""

from __future__ import annotations

import logging
import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path

from sts.utils.cmdline import run


@dataclass
class ProcessInfo:
    """Process information.

    This class provides functionality for managing process information:
    - Process metadata
    - Process status
    - Process control

    Args:
        pid: Process ID (optional, discovered from name)
        name: Process name (optional, discovered from pid)
        status: Process status (optional, discovered from process)
        cmdline: Process command line (optional, discovered from process)

    Example:
        ```python
        info = ProcessInfo()  # Discovers first available process
        info = ProcessInfo(pid=1234)  # Discovers other values
        info = ProcessInfo(name='sleep')  # Discovers matching process
        ```
    """

    # Optional parameters
    pid: int | None = None
    name: str | None = None
    status: str | None = None
    cmdline: str | None = None

    def __post_init__(self) -> None:
        """Initialize process information.

        Discovers process information based on provided parameters.
        """
        # If no parameters provided, get first available process
        if not any([self.pid, self.name]):
            # Get list of process directories
            try:
                proc_entries = [entry for entry in Path('/proc').iterdir() if entry.is_dir()]
            except OSError:
                return

            # Find first numeric directory
            for entry in proc_entries:
                if entry.name.isdigit():
                    self.pid = int(entry.name)
                    break

        # If name provided but no pid, find matching process
        elif self.name and not self.pid:
            # Get list of process directories
            try:
                proc_entries = [entry for entry in Path('/proc').iterdir() if entry.is_dir()]
            except OSError:
                return

            # Find process with matching name
            for entry in proc_entries:
                if not entry.name.isdigit():
                    continue
                comm_path = entry / 'comm'
                try:
                    if comm_path.exists() and comm_path.read_text().strip() == self.name:
                        self.pid = int(entry.name)
                        break
                except (OSError, ValueError):
                    continue

        # If pid found or provided, get other information
        if self.pid:
            proc_path = Path('/proc') / str(self.pid)

            try:
                # Get process name if not provided
                if not self.name:
                    comm_path = proc_path / 'comm'
                    if comm_path.exists():
                        self.name = comm_path.read_text().strip()

                # Get process status
                status_path = proc_path / 'status'
                if status_path.exists():
                    status_content = status_path.read_text().splitlines()
                    for line in status_content:
                        if line.startswith('State:'):
                            self.status = line.split(':')[1].strip()
                            break

                # Get process command line
                cmdline_path = proc_path / 'cmdline'
                if cmdline_path.exists():
                    self.cmdline = cmdline_path.read_text().strip('\x00').replace('\x00', ' ')

            except OSError:
                logging.exception(f'Failed to get process info for PID {self.pid}')

    @property
    def exists(self) -> bool:
        """Check if process exists.

        Returns:
            True if exists, False otherwise

        Example:
            ```python
            info = ProcessInfo(pid=1234)
            info.exists
            True
            ```
        """
        return bool(self.pid and Path('/proc', str(self.pid)).exists())

    @property
    def running(self) -> bool:
        """Check if process is running.

        Returns:
            True if running, False otherwise

        Example:
            ```python
            info = ProcessInfo(pid=1234)
            info.running
            True
            ```
        """
        if not self.pid:
            return False

        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            # Process exists but we don't have permission to send signals
            return True
        return True

    def kill(self, timeout: float = 1.0) -> bool:
        """Kill process.

        Args:
            timeout: Timeout in seconds between SIGTERM and SIGKILL

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            info = ProcessInfo(pid=1234)
            info.kill()
            True
            ```
        """
        if not self.pid:
            return False

        if not self.running:
            return True

        try:
            # Try SIGTERM first
            os.kill(self.pid, signal.SIGTERM)
            time.sleep(timeout)

            # If still running, use SIGKILL
            if self.running:
                os.kill(self.pid, signal.SIGKILL)
                time.sleep(timeout)

                # Check if process is still running
                if self.running:
                    logging.error(f'Failed to kill process {self.pid}')
                    return False

        except ProcessLookupError:
            # Process already terminated
            pass
        except PermissionError:
            logging.exception(f'Permission denied killing process {self.pid}')
            return False

        return True

    @classmethod
    def from_pid(cls, pid: int) -> ProcessInfo | None:
        """Get process information by PID.

        Args:
            pid: Process ID

        Returns:
            Process information or None if not found

        Example:
            ```python
            info = ProcessInfo.from_pid(1234)
            info.status
            'running'
            ```
        """
        info = cls(pid=pid)
        return info if info.exists else None

    @classmethod
    def from_name(cls, name: str) -> ProcessInfo | None:
        """Get process information by name.

        Args:
            name: Process name

        Returns:
            Process information or None if not found

        Example:
            ```python
            info = ProcessInfo.from_name('sleep')
            info.pid
            1234
            ```
        """
        info = cls(name=name)
        return info if info.exists else None


class ProcessManager:
    """Process manager functionality.

    This class provides functionality for managing system processes:
    - Process control
    - Process monitoring
    - Process information

    Example:
        ```python
        pm = ProcessManager()
        pm.kill_all('sleep')
        True
        ```
    """

    def __init__(self) -> None:
        """Initialize process manager."""
        self.proc_path = Path('/proc')

    def get_all(self) -> list[ProcessInfo]:
        """Get list of all processes.

        Returns:
            List of process information

        Example:
            ```python
            pm = ProcessManager()
            pm.get_all()
            [ProcessInfo(pid=1, ...), ProcessInfo(pid=2, ...)]
            ```
        """
        processes = []

        try:
            # Get list of process directories
            proc_entries = [entry for entry in self.proc_path.iterdir() if entry.is_dir()]

            # Filter numeric directories and create processes
            for entry in proc_entries:
                if entry.name.isdigit():
                    pid = int(entry.name)
                    if info := ProcessInfo.from_pid(pid):
                        processes.append(info)

        except OSError:
            logging.exception('Failed to get process list')
            return []

        return processes

    def get_by_name(self, name: str) -> list[ProcessInfo]:
        """Get processes by name.

        Args:
            name: Process name

        Returns:
            List of matching processes

        Example:
            ```python
            pm = ProcessManager()
            pm.get_by_name('sleep')
            [ProcessInfo(pid=1234, name='sleep', ...)]
            ```
        """
        return [p for p in self.get_all() if p.name == name]

    def kill_all(self, name: str, timeout: float = 1.0) -> bool:
        """Kill all processes by name.

        Args:
            name: Process name
            timeout: Timeout in seconds between SIGTERM and SIGKILL

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pm = ProcessManager()
            pm.kill_all('sleep')
            True
            ```
        """
        result = run(f'killall {name}')
        if result.failed:
            return False

        # Wait for processes to finish
        time.sleep(timeout)

        # Check if any processes still running
        return not bool(self.get_by_name(name))
