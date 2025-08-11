# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test command execution module."""

from typing import Any
from unittest.mock import patch

from sts.utils.cmdline import exists, format_arg, format_args, run


def test_run(
    mock_command_result: Any,
    mock_run_with_result: tuple[list[str], dict[str, Any]],
) -> None:
    """Test command execution."""
    calls, results = mock_run_with_result
    with patch('sts.utils.cmdline.logging') as mock_logging:
        # Test basic command
        results['ls -l'] = mock_command_result(stdout='test output')
        result = run('ls -l')
        assert result.succeeded
        assert result.stdout == 'test output'
        assert calls == ['ls -l']
        mock_logging.info.assert_called_once_with("Running: 'ls -l'")

        # Test with custom message
        calls.clear()
        mock_logging.info.reset_mock()
        results['ls -l'] = mock_command_result(stdout='test output')
        result = run('ls -l', msg='Listing files')
        assert result.succeeded
        assert result.stdout == 'test output'
        assert calls == ['ls -l']
        mock_logging.info.assert_called_once_with("Listing files: 'ls -l'")


def test_format_arg_string() -> None:
    """Test string argument formatting."""
    assert format_arg('size', '1G') == "--size='1G'"
    assert format_arg('path', '/tmp/test') == "--path='/tmp/test'"
    assert format_arg('name', 'test file') == "--name='test file'"


def test_format_arg_number() -> None:
    """Test number argument formatting."""
    assert format_arg('count', 5) == "--count='5'"
    assert format_arg('size', 1.5) == "--size='1.5'"


def test_format_arg_bool() -> None:
    """Test boolean argument formatting."""
    assert format_arg('quiet', True) == '--quiet'
    assert format_arg('verbose', False) == ''


def test_format_arg_none() -> None:
    """Test None argument formatting."""
    assert format_arg('size', None) == ''


def test_format_arg_list() -> None:
    """Test list argument formatting."""
    assert format_arg('names', ['a', 'b']) == "--names='a' --names='b'"
    assert format_arg('sizes', [1, 2]) == "--sizes='1' --sizes='2'"
    assert format_arg('values', [1.5, 2.5]) == "--values='1.5' --values='2.5'"


def test_format_arg_underscore() -> None:
    """Test underscore to dash conversion."""
    assert format_arg('block_size', '1M') == "--block-size='1M'"
    assert format_arg('max_size', 100) == "--max-size='100'"


def test_format_args_empty() -> None:
    """Test empty arguments formatting."""
    assert format_args() == ''


def test_format_args_single() -> None:
    """Test single argument formatting."""
    assert format_args(size='1G') == "--size='1G'"
    assert format_args(quiet=True) == '--quiet'
    assert format_args(verbose=False) == ''
    assert format_args(count=5) == "--count='5'"


def test_format_args_multiple() -> None:
    """Test multiple arguments formatting."""
    args = format_args(
        size='1G',
        quiet=True,
        verbose=False,
        count=5,
        names=['a', 'b'],
        block_size='1M',
    )
    assert '--size=' in args
    assert '--quiet' in args
    assert '--verbose' not in args
    assert '--count=' in args
    assert "--names='a'" in args
    assert "--names='b'" in args
    assert '--block-size=' in args


def test_exists() -> None:
    """Test command existence check."""
    with patch('sts.utils.cmdline.host') as mock_host:
        mock_host.exists.side_effect = [True, False]
        assert exists('ls')
        assert not exists('nonexistent')
