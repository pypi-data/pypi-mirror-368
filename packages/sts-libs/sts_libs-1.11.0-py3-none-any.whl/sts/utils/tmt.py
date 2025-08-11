# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test Management Tool utilities.

This module provides functionality for working with tmt:
- Test result management
- Log gathering
- Duration calculation
- Custom result submission

For more information about tmt, see:
https://tmt.readthedocs.io/en/stable/spec/tests.html#result
https://tmt.readthedocs.io/en/stable/spec/plans.html#spec-plans-results
"""

from __future__ import annotations

import json
import logging
import tarfile
import time
from os import getenv
from pathlib import Path
from typing import Any, Literal, TypedDict
from uuid import uuid4

# Get test data path from environment or generate unique path
test_data_path = getenv('TMT_TEST_DATA')
if not test_data_path:
    dir_name = str(uuid4())
    logging.warning(f"TMT_TEST_DATA env var not detected. Using '/var/tmp/{dir_name}'")
    test_data_path = dir_name

TMT_TEST_DATA = Path(test_data_path)


def gather_logs_from_dir(logs_path: str, name: str | None) -> Path | None:
    """Gather logs from directory into a tarfile.

    Args:
        logs_path: Path to directory containing logs
        name: Name for the tarfile (optional)

    Returns:
        Path to created tarfile or None if directory doesn't exist

    Example:
        ```python
        gather_logs_from_dir('/var/log/messages', 'system_logs')
        Path('/var/tmp/uuid/system_logs.tar')
        ```
    """
    path = Path(logs_path)
    if not path.is_dir():
        return None

    # Generate tarfile name
    if not name:
        name = str(path).replace('/', '_')
    if '.tar' not in name:
        name = f'{name}.tar'

    # Create tarfile
    tarfile_path = f'{TMT_TEST_DATA}/{name}'
    with tarfile.open(tarfile_path, 'w') as tar:
        tar.add(path, recursive=True)
    return Path(tarfile_path)


def timestamp() -> float:
    """Get current timestamp.

    Returns:
        Current time in seconds since epoch

    Example:
        ```python
        timestamp()
        1677721600.0
        ```
    """
    return time.time()


def calculate_duration(start: float, end: float) -> str:
    """Calculate duration between timestamps.

    Args:
        start: Start timestamp
        end: End timestamp

    Returns:
        Duration in hh:mm:ss format

    Example:
        ```python
        calculate_duration(1677721600.0, 1677725200.0)
        '01:00:00'
        ```
    """
    secs = int(end - start)
    return f'{secs // 3600:02d}:{secs % 3600 // 60:02d}:{secs % 60:02d}'


class GuestType(TypedDict):
    """Guest information type.

    Attributes:
        name: Guest name
        role: Guest role
    """

    name: str | None
    role: str | None


# Valid TMT result types
TmtResult = Literal['pass', 'fail', 'info', 'warn', 'error']


class CustomResults(TypedDict):
    """Custom test results type.

    Attributes:
        name: Result name (e.g. "/step-1" or "/setup/iscsi/target")
        result: Test result
        note: Additional notes
        log: Paths to log files
        serialnumber: Serial number in test sequence
        guest: Guest information
        duration: Test duration
        ids: Additional identifiers
    """

    name: str
    result: TmtResult
    note: str | None
    log: list[str] | None
    serialnumber: int | None
    guest: GuestType | None
    duration: str | None
    ids: dict[str, str] | None


def remove_nones(cr: CustomResults) -> dict[str, Any]:
    """Remove None values from custom results.

    Args:
        cr: Custom results dictionary

    Returns:
        Dictionary with None values removed

    Example:
        ```python
        remove_nones({'name': 'test', 'note': None, 'result': 'pass'})
        {'name': 'test', 'result': 'pass'}
        ```
    """
    return {k: v for k, v in cr.items() if v is not None}


class Results:
    """TMT test results management.

    This class provides functionality for managing TMT test results:
    - Adding test results
    - Managing logs
    - Calculating durations
    - Submitting results

    Example:
        ```python
        results = Results()
        results.add(name='setup', result='pass')
        results.add(name='test', result='pass', log=['test.log'])
        results.submit()
        ```
    """

    def __init__(self) -> None:
        """Initialize results manager."""
        self.results: list[dict[str, Any]] = []
        self.timestamp = timestamp()

    def add(
        self,
        name: str = '/',
        result: TmtResult = 'pass',
        note: str | None = None,
        log: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        """Add test result.

        When TMT plan is set to 'result: custom', use this followed by submit()
        to create the necessary result.json. Use multiple times when test has
        distinctive steps (parts).

        Args:
            name: Result name (e.g. '/setup/something' or 'setup')
            result: Test result
            note: Additional notes
            log: Paths to log files (relative to TMT_TEST_DATA)
            errors: Error messages (sets result to 'fail' if present)

        Example:
            ```python
            results = Results()
            results.add(
                name='setup',
                result='pass',
                log=['setup.log'],
            )
            ```
        """
        if not name.startswith('/'):
            name = f'/{name}'
        if errors:
            result = 'fail'

        # Calculate duration
        new_timestamp = timestamp()
        duration = calculate_duration(self.timestamp, new_timestamp)
        self.timestamp = new_timestamp

        # Create result
        result_to_add = CustomResults(
            name=name,
            result=result,
            note=note,
            log=log,
            duration=duration,
            ids=None,
            serialnumber=None,
            guest=None,
        )

        self.results.append(remove_nones(result_to_add))

    def submit(self) -> None:
        """Submit test results.

        Creates results.json file in TMT_TEST_DATA directory.

        Example:
            ```python
            results = Results()
            results.add(name='test', result='pass')
            results.submit()  # Creates results.json
            ```
        """
        file = Path(TMT_TEST_DATA / 'results.json')
        with file.open('w') as f:
            json.dump(self.results, f)
