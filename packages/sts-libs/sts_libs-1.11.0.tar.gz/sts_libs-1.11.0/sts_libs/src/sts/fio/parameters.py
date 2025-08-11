# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""FIO parameter configurations."""

from __future__ import annotations

import configparser
import logging
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pathlib import Path

# Type aliases
IOEngine = Literal['libaio', 'sync', 'posixaio', 'mmap', 'splice']
RWType = Literal['read', 'write', 'randread', 'randwrite', 'randrw', 'trim']
VerifyType = Literal['crc32', 'md5', 'sha1', 'sha256', 'sha512', 'meta']

# Export classes
__all__ = [
    'BlockDeviceParameters',
    'DefaultParameters',
    'FIOParameters',
    'FileSystemParameters',
    'StressParameters',
]


@dataclass
class FIOParameters:
    """Base FIO parameters.

    This class provides common parameters for FIO operations:
    - Basic I/O settings
    - Job control
    - Verification options

    Args:
        name: Job name (optional, defaults to 'sts-fio')
        filename: Target file or device (optional)
        ioengine: I/O engine to use (optional, defaults to 'libaio')
        direct: Use direct I/O (optional, defaults to True)
        rw: Read/write mode (optional, defaults to 'randrw')
        bs: Block size (optional, defaults to '4k')
        numjobs: Number of jobs (optional, defaults to 1)
        size: Total size (optional)
        runtime: Runtime in seconds (optional)
        iodepth: I/O depth (optional)
        group_reporting: Enable group reporting (optional)
        verify: Verification method (optional)
        verify_fatal: Exit on verification failure (optional)
        verify_backlog: Verify backlog size (optional)
        end_fsync: Sync at end of job (optional)

    Example:
        ```python
        params = FIOParameters()  # Uses defaults
        params = FIOParameters(name='test', rw='read')  # Custom settings
        ```
    """

    # Optional parameters with defaults
    name: str = 'sts-fio'
    ioengine: IOEngine = 'libaio'
    direct: bool = True
    rw: RWType = 'randrw'
    bs: str = '4k'
    numjobs: int = 1
    group_reporting: bool = False
    verify_fatal: bool = False
    end_fsync: bool = False

    # Optional parameters without defaults
    filename: str | None = None
    size: str | None = None
    runtime: int | None = None
    iodepth: int | None = None
    verify: VerifyType | None = None
    verify_backlog: int | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert parameters to FIO command format.

        Returns:
            Dictionary of FIO parameters

        Example:
            ```python
            params.to_dict()
            {'name': 'test', 'ioengine': 'libaio', 'direct': '1', ...}
            ```
        """
        result: dict[str, str] = {}
        for key, value in asdict(self).items():
            if value is None:
                continue
            if isinstance(value, bool):
                if value:
                    result[key] = '1'
            else:
                result[key] = str(value)
        return result

    @classmethod
    def from_file(cls, path: str | Path) -> FIOParameters | None:
        """Create parameters from FIO config file.

        Args:
            path: Path to FIO config file

        Returns:
            FIOParameters instance or None if invalid

        Example:
            ```python
            params = FIOParameters.from_file('test.fio')
            ```
        """
        try:
            config = configparser.ConfigParser()
            config.read(path)

            # Get the first job section
            job_section = next(s for s in config.sections() if s != 'global')
            params = dict(config[job_section])

            # Convert parameters
            return cls(
                name=job_section,
                **{k: v for k, v in params.items() if not k.startswith('_')},  # type: ignore[arg-type]
            )
        except (configparser.Error, StopIteration) as e:
            logging.warning(f'Invalid config file: {e}')
            return None


@dataclass
class DefaultParameters(FIOParameters):
    """Default FIO parameters.

    This class provides default parameters for general FIO testing:
    - Random read/write with verification
    - Single job with moderate I/O depth
    - Short runtime for quick testing

    Example:
        ```python
        params = DefaultParameters()  # Uses defaults
        params = DefaultParameters(name='test')  # Custom name
        ```
    """

    # Override defaults
    group_reporting: bool = True
    verify_fatal: bool = True

    # Set additional defaults
    iodepth: int = field(default=32, init=False)  # type: ignore[assignment]
    runtime: int = field(default=60, init=False)  # type: ignore[assignment]
    verify: VerifyType = field(default='crc32', init=False)  # type: ignore[assignment]
    verify_backlog: int = field(default=1024, init=False)  # type: ignore[assignment]


@dataclass
class FileSystemParameters(FIOParameters):
    """Filesystem-specific FIO parameters.

    This class provides parameters optimized for filesystem testing:
    - Sequential write operations
    - Large block size for better throughput
    - Single job with direct I/O
    - End sync for data durability

    Example:
        ```python
        params = FileSystemParameters()  # Uses defaults
        params = FileSystemParameters(name='test')  # Custom name
        ```
    """

    # Override defaults
    ioengine: IOEngine = 'sync'
    rw: RWType = 'write'
    bs: str = '1M'
    end_fsync: bool = True

    # Set additional defaults
    size: str = field(default='10G', init=False)  # type: ignore[assignment]


@dataclass
class BlockDeviceParameters(FIOParameters):
    """Block device-specific FIO parameters.

    This class provides parameters optimized for block device testing:
    - Random read operations
    - Small block size for IOPS testing
    - Multiple jobs with high I/O depth
    - Long runtime for stability testing

    Example:
        ```python
        params = BlockDeviceParameters()  # Uses defaults
        params = BlockDeviceParameters(name='test')  # Custom name
        ```
    """

    # Override defaults
    rw: RWType = 'randread'
    bs: str = '512'
    numjobs: int = 4
    group_reporting: bool = True

    # Set additional defaults
    iodepth: int = field(default=32, init=False)  # type: ignore[assignment]
    runtime: int = field(default=1800, init=False)  # type: ignore[assignment]


@dataclass
class StressParameters(FIOParameters):
    """Stress testing FIO parameters.

    This class provides parameters for stress testing:
    - Random read/write with high concurrency
    - Multiple jobs with high I/O depth
    - Long runtime for endurance testing
    - Sequential mapping for performance

    Example:
        ```python
        params = StressParameters()  # Uses defaults
        params = StressParameters(name='test')  # Custom name
        ```
    """

    # Override defaults
    numjobs: int = 64
    group_reporting: bool = True

    # Set additional defaults
    iodepth: int = field(default=64, init=False)  # type: ignore[assignment]
    runtime: int = field(default=3600, init=False)  # type: ignore[assignment]
