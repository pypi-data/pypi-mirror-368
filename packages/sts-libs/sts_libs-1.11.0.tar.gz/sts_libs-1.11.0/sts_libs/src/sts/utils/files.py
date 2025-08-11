# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""File operations module.

This module provides functionality for file system operations:
- Directory validation
- File counting
- Path operations
- Mount management
- Filesystem operations
"""

from __future__ import annotations

import logging
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING

from sts import get_sts_host
from sts.utils.cmdline import run
from sts.utils.errors import STSError

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator

    from testinfra.host import Host


host: Host = get_sts_host()


class DirectoryError(STSError):
    """Base class for directory-related errors."""


class DirNotFoundError(DirectoryError):
    """Directory does not exist."""


class DirTypeError(DirectoryError):
    """Path exists but is not a directory."""


class DirAccessError(DirectoryError):
    """Directory cannot be accessed."""


@dataclass
class Directory:
    """Directory representation.

    Provides functionality for directory operations including:
    - Existence checking
    - File counting
    - Path resolution

    Args:
        path: Directory path (optional, defaults to current directory)
        create: Create directory if it doesn't exist (optional)
        mode: Directory creation mode (optional)

    Example:
        ```python
        dir = Directory()  # Uses current directory
        dir = Directory('/tmp/test')  # Uses specific path
        dir = Directory('/tmp/test', create=True)  # Creates if needed
        ```
    """

    # Required parameters
    path: Path = field(default_factory=Path.cwd)

    # Optional parameters
    create: bool = False
    mode: int = 0o755

    def __post_init__(self) -> None:
        """Initialize directory.

        Creates directory if needed.
        """
        # Create directory if needed
        if self.create and not self.exists:
            try:
                self.path.mkdir(mode=self.mode, parents=True, exist_ok=True)
            except OSError:
                logging.exception('Failed to create directory')

    @property
    def exists(self) -> bool:
        """Check if directory exists and is a directory."""
        return self.path.is_dir()

    def validate(self) -> None:
        """Validate directory exists and is accessible.

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
        """
        if not self.path.exists():
            raise DirNotFoundError(f'Directory not found: {self.path}')
        if not self.exists:
            raise DirTypeError(f'Not a directory: {self.path}')

    def iter_files(self, *, recursive: bool = False) -> Iterator[Path]:
        """Iterate over files in directory.

        Args:
            recursive: If True, recursively iterate through subdirectories

        Yields:
            Path objects for each file

        Raises:
            DirAccessError: If directory cannot be accessed
        """
        try:
            if recursive:
                for item in self.path.rglob('*'):
                    if item.is_file():
                        yield item
            else:
                for item in self.path.iterdir():
                    if item.is_file():
                        yield item
        except PermissionError as e:
            logging.exception(f'Permission denied accessing {self.path}')
            raise DirAccessError(f'Permission denied: {self.path}') from e
        except OSError as e:
            logging.exception(f'Error accessing {self.path}')
            raise DirAccessError(f'Error accessing directory: {e}') from e

    @staticmethod
    def should_remove_file_with_pattern(file: Path, pattern: str) -> bool:
        """Check if file should be removed because it contains pattern.

        Args:
            file: File to check
            pattern: Pattern to match in file contents

        Returns:
            True if file contains pattern and should be removed
        """
        try:
            content = file.read_text()
        except (OSError, UnicodeDecodeError):
            logging.exception(f'Error reading {file}')
            return False
        return pattern in content

    @staticmethod
    def should_remove_file_without_pattern(file: Path, pattern: str) -> bool:
        """Check if file should be removed because it does not contain pattern.

        Args:
            file: File to check
            pattern: Pattern to match in file contents

        Returns:
            True if file does not contain pattern and should be removed
        """
        try:
            content = file.read_text()
        except (OSError, UnicodeDecodeError):
            logging.exception(f'Error reading {file}')
            return False
        return pattern not in content

    @staticmethod
    def remove_file(file: Path) -> None:
        """Remove file safely.

        Args:
            file: File to remove
        """
        try:
            file.unlink()
        except OSError:
            logging.exception(f'Error removing {file}')

    def count_files(self) -> int:
        """Count number of files in directory.

        Returns:
            Number of files in directory (excluding directories)

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
            DirAccessError: If directory cannot be accessed

        Example:
            ```python
            Directory('/etc').count_files()
            42
            ```
        """
        self.validate()
        return sum(1 for _ in self.iter_files())

    def rm_files_containing(self, pattern: str, *, invert: bool = False) -> None:
        """Delete files containing (or not containing) specific pattern.

        Args:
            pattern: Pattern to match in file contents
            invert: Delete files NOT containing pattern

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
            DirAccessError: If directory cannot be accessed

        Example:
            ```python
            Directory('/tmp').rm_files_containing('error')  # Remove files containing 'error'
            Directory('/tmp').rm_files_containing('error', invert=True)  # Remove files NOT containing 'error'
            ```
        """
        self.validate()
        check_func = self.should_remove_file_without_pattern if invert else self.should_remove_file_with_pattern
        for file in self.iter_files():
            if check_func(file, pattern):
                self.remove_file(file)

    def remove_dir(self) -> None:
        """Remove directory and all its contents using shutil.rmtree.

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
            DirAccessError: If directory cannot be accessed

        Example:
            ```python
            Directory(Path('/tmp/test')).remove_dir()
            ```
        """
        self.validate()
        try:
            rmtree(self.path)
        except (OSError, PermissionError):
            logging.exception(f'Error removing {self.path}')


@contextmanager
def change_directory(path: Path) -> Generator[None, None, None]:
    """Context manager to temporarily change working directory.

    Changes to the specified directory and automatically restores
    the original working directory when exiting the context, even
    if an exception occurs.

    Args:
        path: Directory to change to

    Yields:
        None

    Example:
        ```python
        with change_directory(Path('/tmp')):
            # Working directory is now /tmp
            result = run('pwd')  # Shows /tmp
        # Working directory is restored to original
        ```
    """
    original_cwd = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_cwd)


def count_files(directory: str | Path | None = None) -> int:
    """Count number of files in directory.

    Args:
        directory: Path to directory to count files in (optional)

    Returns:
        Number of files in directory (excluding directories)

    Raises:
        DirNotFoundError: If directory does not exist
        DirTypeError: If path exists but is not a directory
        DirAccessError: If directory cannot be accessed

    Example:
        ```python
        count_files()  # Count files in current directory
        count_files('/etc')  # Count files in specific directory
        ```
    """
    path = Path(directory) if directory else Path.cwd()
    return Directory(path).count_files()


def rm_files_containing(directory: str | Path | None = None, pattern: str = '', *, invert: bool = False) -> None:
    """Delete files containing (or not containing) specific pattern.

    Args:
        directory: Directory to search in (optional)
        pattern: Pattern to match in file contents (optional)
        invert: Delete files NOT containing pattern (optional)

    Raises:
        DirNotFoundError: If directory does not exist
        DirTypeError: If path exists but is not a directory
        DirAccessError: If directory cannot be accessed

    Example:
        ```python
        rm_files_containing()  # Remove all files in current directory
        rm_files_containing('/tmp', 'error')  # Remove files containing 'error'
        rm_files_containing('/tmp', 'error', invert=True)  # Remove files NOT containing 'error'
        ```
    """
    path = Path(directory) if directory else Path.cwd()
    Directory(path).rm_files_containing(pattern, invert=invert)


def is_mounted(device: str | None = None, mountpoint: str | None = None) -> bool:
    """Check if device or mountpoint is mounted.

    Args:
        device: Device to check (optional)
        mountpoint: Mountpoint to check (optional)

    Returns:
        True if mounted, False otherwise

    Example:
        ```python
        is_mounted(device='/dev/sda1')
        True
        is_mounted(mountpoint='/mnt')
        False
        ```
    """
    if device:
        return run(f'mount | grep {device}').succeeded
    if mountpoint:
        return run(f'mount | grep {mountpoint}').succeeded
    return False


def mount(
    device: str | None = None,
    mountpoint: str | None = None,
    fs_type: str | None = None,
    options: str | None = None,
) -> bool:
    """Mount device at mountpoint.

    Args:
        device: Device to mount (optional)
        mountpoint: Mountpoint to mount at (optional)
        fs_type: Filesystem type (optional)
        options: Mount options (optional)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        mount('/dev/sda1', '/mnt')  # Basic mount
        mount('/dev/sda1', '/mnt', 'ext4', 'ro')  # Mount with options
        ```
    """
    cmd = ['mount']
    if fs_type:
        cmd.extend(['-t', fs_type])
    if options:
        cmd.extend(['-o', options])
    if device:
        cmd.append(device)
    if mountpoint:
        Directory(Path(mountpoint), create=True)
        cmd.append(mountpoint)

    result = run(' '.join(cmd))
    if result.failed:
        logging.error(f'Failed to mount device: {result.stderr}')
        return False
    return True


def umount(device: str | None = None, mountpoint: str | None = None) -> bool:
    """Unmount device or mountpoint.

    Args:
        device: Device to unmount (optional)
        mountpoint: Mountpoint to unmount (optional)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        umount('/dev/sda1')  # Unmount device
        umount(mountpoint='/mnt')  # Unmount mountpoint
        ```
    """
    if device and not is_mounted(device=device):
        return True
    if mountpoint and not is_mounted(mountpoint=mountpoint):
        return True

    cmd = ['umount']
    if device:
        cmd.append(device)
    if mountpoint:
        cmd.append(mountpoint)

    result = run(' '.join(cmd))
    if result.failed:
        logging.error(f'Failed to unmount device: {result.stderr}')
        return False
    return True


def mkfs(device: str | None = None, fs_type: str | None = None, *, force: bool = False) -> bool:
    """Create filesystem on device.

    Args:
        device: Device to create filesystem on (optional)
        fs_type: Filesystem type (optional)
        force: Force creation even if filesystem exists (optional)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        mkfs('/dev/sda1', 'ext4')  # Create ext4 filesystem
        mkfs('/dev/sda1', 'ext4', force=True)  # Force creation
        ```
    """
    if not device or not fs_type:
        logging.error('Device and filesystem type required')
        return False

    force_option = '-F' if fs_type != 'xfs' else '-f'
    cmd = [f'mkfs.{fs_type}']
    if force:
        cmd.append(force_option)
    cmd.append(device)

    result = run(' '.join(cmd))
    if result.failed:
        logging.error(f'Failed to create {fs_type} filesystem on {device}: {result.stderr}')
        return False
    return True


def get_free_space(path: str | Path | None = None) -> int | None:
    """Get free space in bytes.

    Args:
        path: Path to check free space for (optional)

    Returns:
        Free space in bytes or None if error

    Example:
        ```python
        get_free_space()  # Check current directory
        get_free_space('/mnt')  # Check specific path
        ```
    """
    path_str = str(path) if path else '.'
    result = run(f'df -B 1 {path_str}')
    if result.failed:
        logging.error('Failed to get free space')
        return None

    # Parse output like:
    # Filesystem     1B-blocks       Used   Available Use% Mounted on
    # /dev/sda1    1073741824   10485760  1063256064   1% /mnt
    if match := re.search(r'\S+\s+\d+\s+\d+\s+(\d+)', result.stdout):
        return int(match.group(1))

    return None
