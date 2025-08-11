# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test configuration and fixtures."""

from collections.abc import Generator
from dataclasses import dataclass

import pytest


@dataclass
class MockCommandResult:
    """Mock command result for testing.

    This class mimics testinfra's CommandResult for testing purposes.
    It provides the same interface but with simpler implementation.
    """

    rc: int = 0
    stdout: str = ''
    stderr: str = ''
    command: str = ''

    @property
    def succeeded(self) -> bool:
        """Return True if command succeeded."""
        return self.rc == 0

    @property
    def failed(self) -> bool:
        """Return True if command failed."""
        return not self.succeeded


@pytest.fixture
def mock_command_result() -> type[MockCommandResult]:
    """Provide mock command result class.

    Returns:
        MockCommandResult class

    Example:
        def test_something(mock_command_result):
            result = mock_command_result(stdout='test')
            assert result.stdout == 'test'
    """
    return MockCommandResult


@pytest.fixture
def mock_run(monkeypatch: pytest.MonkeyPatch) -> Generator[list[str], None, None]:
    """Mock command execution.

    This fixture provides a way to track executed commands and mock their results.
    It automatically patches the host.run function used by the codebase.

    Example:
        def test_something(mock_run):
            # Run your code that executes commands
            assert mock_run.calls == ['expected command']
    """
    calls: list[str] = []

    def _mock_run(cmd: str) -> MockCommandResult:
        calls.append(cmd)
        return MockCommandResult()

    monkeypatch.setattr('sts.utils.cmdline.host.run', _mock_run)
    return calls


@pytest.fixture
def mock_run_with_result(
    mock_command_result: type[MockCommandResult],
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[tuple[list[str], dict[str, MockCommandResult]], None, None]:
    r"""Mock command execution with custom results.

    This fixture provides a way to specify custom results for specific commands.
    Commands not in the results dict will return a default success result.

    Example:
        def test_something(mock_run_with_result):
            calls, results = mock_run_with_result
            results['ls -l'] = mock_command_result(stdout='file1\nfile2\n')
            # Run your code that executes 'ls -l'
            assert calls == ['ls -l']
    """
    calls: list[str] = []
    results: dict[str, MockCommandResult] = {}

    def _mock_run(cmd: str) -> MockCommandResult:
        calls.append(cmd)
        return results.get(cmd, mock_command_result())

    monkeypatch.setattr('sts.utils.cmdline.host.run', _mock_run)
    return calls, results
