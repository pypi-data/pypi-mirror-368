# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for Stratis filesystem management.

This module tests:
- Filesystem report parsing
- Filesystem operations
- Snapshot management
"""

from typing import Any

import pytest

from sts.stratis.filesystem import FilesystemReport, StratisFilesystem


class TestFilesystemReport:
    """Test FilesystemReport class."""

    def test_from_dict(self) -> None:
        """Test creating filesystem report from dictionary."""
        data = {
            'name': 'fs1',
            'uuid': '123e4567-e89b-12d3-a456-426614174000',
            'size': '10G',
            'size_limit': '20G',
            'origin': 'fs0',
            'used': '5G',
        }
        report = FilesystemReport.from_dict(data)
        assert report is not None
        assert report.name == 'fs1'
        assert report.uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert report.size == '10G'
        assert report.size_limit == '20G'
        assert report.origin == 'fs0'
        assert report.used == '5G'

    def test_from_dict_missing_fields(self) -> None:
        """Test creating filesystem report with missing fields."""
        data = {'name': 'fs1'}
        report = FilesystemReport.from_dict(data)
        assert report is not None
        assert report.name == 'fs1'
        assert report.uuid is None
        assert report.size is None
        assert report.size_limit is None
        assert report.origin is None
        assert report.used is None

    def test_from_dict_invalid(self) -> None:
        """Test creating filesystem report from invalid dictionary."""
        data = {'invalid': 'data'}
        report = FilesystemReport.from_dict(data)
        assert report is not None
        assert report.name is None
        assert report.uuid is None
        assert report.size is None
        assert report.size_limit is None
        assert report.origin is None
        assert report.used is None


@pytest.mark.usefixtures('mock_command_result')
class TestStratisFilesystem:
    """Test StratisFilesystem class."""

    def test_init_defaults(self) -> None:
        """Test default filesystem values."""
        fs = StratisFilesystem()
        assert fs.name is None
        assert fs.pool_name is None
        assert fs.uuid is None
        assert fs.size is None
        assert fs.size_limit is None
        assert fs.origin is None
        assert fs.used is None

    def test_init_custom(self) -> None:
        """Test custom filesystem values."""
        fs = StratisFilesystem(
            name='fs1',
            pool_name='pool1',
            uuid='123e4567-e89b-12d3-a456-426614174000',
            size=1000000000,
            size_limit='20G',
            origin='fs0',
            used='5G',
        )
        assert fs.name == 'fs1'
        assert fs.pool_name == 'pool1'
        assert fs.uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert fs.size == 1000000000
        assert fs.size_limit == '20G'
        assert fs.origin == 'fs0'
        assert fs.used == '5G'

    def test_from_report(self) -> None:
        """Test creating filesystem from report."""
        report = FilesystemReport(
            name='fs1',
            uuid='123e4567-e89b-12d3-a456-426614174000',
            size='10G',
            size_limit='20G',
            origin='fs0',
            used='5G',
        )
        fs = StratisFilesystem.from_report(report, 'pool1')
        assert fs is not None
        assert fs.name == 'fs1'
        assert fs.pool_name == 'pool1'
        assert fs.uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert fs.size_limit == '20G'
        assert fs.origin == 'fs0'
        assert fs.used == '5G'

    def test_from_report_invalid(self) -> None:
        """Test creating filesystem from invalid report."""
        report = FilesystemReport()  # No name
        fs = StratisFilesystem.from_report(report, 'pool1')
        assert fs is None

    def test_create_filesystem(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test filesystem creation."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis filesystem create pool1 fs1'] = mock_command_result()

        fs = StratisFilesystem(name='fs1', pool_name='pool1')
        assert fs.create() is True
        assert calls[-1] == 'stratis filesystem create pool1 fs1'

    def test_create_filesystem_with_size(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test filesystem creation with size."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis filesystem create --size 10G --size-limit 20G pool1 fs1'] = mock_command_result()

        fs = StratisFilesystem(name='fs1', pool_name='pool1')
        assert fs.create(size='10G', size_limit='20G') is True
        assert calls[-1] == 'stratis filesystem create --size 10G --size-limit 20G pool1 fs1'

    def test_destroy_filesystem(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test filesystem destruction."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis filesystem destroy pool1 fs1'] = mock_command_result()

        fs = StratisFilesystem(name='fs1', pool_name='pool1')
        assert fs.destroy() is True
        assert calls[-1] == 'stratis filesystem destroy pool1 fs1'

    def test_rename_filesystem(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test filesystem renaming."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis filesystem rename pool1 fs1 fs2'] = mock_command_result()

        fs = StratisFilesystem(name='fs1', pool_name='pool1')
        assert fs.rename('fs2') is True
        assert calls[-1] == 'stratis filesystem rename pool1 fs1 fs2'
        assert fs.name == 'fs2'

    def test_snapshot_filesystem(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test filesystem snapshot."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(stdout='{"pools": []}')
        results['stratis filesystem snapshot pool1 fs1 snap1'] = mock_command_result()

        fs = StratisFilesystem(name='fs1', pool_name='pool1')
        snap = fs.snapshot('snap1')
        assert snap is not None
        assert snap.name == 'snap1'
        assert snap.pool_name == 'pool1'
        assert snap.origin == 'fs1'
        assert calls[-1] == 'stratis filesystem snapshot pool1 fs1 snap1'

    def test_get_all(
        self,
        mock_run_with_result: tuple[list[str], dict[str, Any]],
        mock_command_result: Any,
    ) -> None:
        """Test getting all filesystems."""
        calls, results = mock_run_with_result
        results['stratis report'] = mock_command_result(
            stdout="""{
            "pools": [
                {
                    "name": "pool1",
                    "filesystems": [
                        {
                            "name": "fs1",
                            "uuid": "123e4567-e89b-12d3-a456-426614174000",
                            "size": "10G",
                            "size_limit": "20G",
                            "origin": null,
                            "used": "5G"
                        }
                    ]
                }
            ]
        }"""
        )

        filesystems = StratisFilesystem.get_all('pool1')
        assert len(filesystems) == 1
        assert filesystems[0].name == 'fs1'
        assert filesystems[0].pool_name == 'pool1'
        assert filesystems[0].uuid == '123e4567-e89b-12d3-a456-426614174000'
        assert filesystems[0].size_limit == '20G'
        assert filesystems[0].origin is None
        assert filesystems[0].used == '5G'
        assert calls == ['stratis report']
