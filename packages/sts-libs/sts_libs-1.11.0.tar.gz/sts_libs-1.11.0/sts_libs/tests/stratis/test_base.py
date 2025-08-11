# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for Stratis base functionality.

This module tests:
- Configuration handling
- Command options
- Base operations
"""

from typing import Any

import pytest

from sts.stratis.base import CLI_NAME, Key, StratisBase, StratisConfig
from sts.stratis.errors import StratisError


class TestStratisConfig:
    """Test StratisConfig class."""

    def test_defaults(self) -> None:
        """Test default configuration values."""
        config = StratisConfig()
        assert config.propagate is False
        assert config.unhyphenated_uuids is False

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = StratisConfig(
            propagate=True,
            unhyphenated_uuids=True,
        )
        assert config.propagate is True
        assert config.unhyphenated_uuids is True

    def test_to_args(self) -> None:
        """Test converting configuration to arguments."""
        config = StratisConfig(propagate=True, unhyphenated_uuids=True)
        args = config.to_args()
        assert '--propagate' in args
        assert '--unhyphenated_uuids' in args


@pytest.mark.usefixtures('mock_command_result')
class TestStratisBase:
    """Test StratisBase class."""

    def test_init_defaults(self) -> None:
        """Test default base values."""
        base = StratisBase()
        assert isinstance(base.config, StratisConfig)
        assert base.config.propagate is False
        assert base.config.unhyphenated_uuids is False
        assert base is not None

    def test_init_custom(self) -> None:
        """Test custom base values."""
        config = StratisConfig(propagate=True, unhyphenated_uuids=True)
        base = StratisBase(config=config)
        assert base.config.propagate is True
        assert base.config.unhyphenated_uuids is True

    @pytest.mark.usefixtures('mock_run')
    def test_run_command_basic(self, mock_run: list[str]) -> None:
        """Test running basic command."""
        base = StratisBase()
        base.run_command('version')
        assert mock_run == [f'{CLI_NAME} version']

    @pytest.mark.usefixtures('mock_run')
    def test_run_command_with_options(self, mock_run: list[str]) -> None:
        """Test running command with options."""
        base = StratisBase()
        base.run_command(
            subcommand='pool',
            action='create',
            options={'--key-desc': 'mykey', '--no-overprovision': None},
            positional_args=['pool1', '/dev/sda'],
        )
        assert mock_run == [f'{CLI_NAME} pool create --key-desc mykey --no-overprovision pool1 /dev/sda']

    def test_run_command_propagate_error(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test error propagation in command."""
        calls, results = mock_run_with_result
        results['stratis --propagate invalid'] = mock_command_result(rc=1, stderr='error')

        base = StratisBase(config=StratisConfig(propagate=True))
        with pytest.raises(StratisError, match='Command failed: error'):
            base.run_command('invalid')
        assert calls[-1] == 'stratis --propagate invalid'

    def test_get_report(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test getting report."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')

        base = StratisBase()
        report = base.get_report()
        assert report == {'pools': []}
        assert calls[-1] == 'stratis report'


@pytest.mark.usefixtures('mock_command_result')
class TestKey:
    """Test Key class."""

    @pytest.mark.usefixtures('mock_run')
    def test_set_key(self, mock_run: list[str]) -> None:
        """Test setting key."""
        key = Key()
        key.set('mykey', '/path/to/keyfile')
        assert mock_run == [f'{CLI_NAME} key set --keyfile-path /path/to/keyfile mykey']

    @pytest.mark.usefixtures('mock_run')
    def test_unset_key(self, mock_run: list[str]) -> None:
        """Test unsetting key."""
        key = Key()
        key.unset('mykey')
        assert mock_run == [f'{CLI_NAME} key unset mykey']

    @pytest.mark.usefixtures('mock_run')
    def test_list_keys(self, mock_run: list[str]) -> None:
        """Test listing keys."""
        key = Key()
        key.list()
        assert mock_run == [f'{CLI_NAME} key list']

    def test_key_exists(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test checking key existence."""
        calls, results = mock_run_with_result
        results[f'{CLI_NAME} key list'] = mock_command_result(stdout='mykey\notherkey\n')

        key = Key()
        assert key.exists('mykey') is True
        assert key.exists('nonexistent') is False
        assert calls == [f'{CLI_NAME} key list', f'{CLI_NAME} key list']
