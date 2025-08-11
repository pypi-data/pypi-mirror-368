# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for NVMe device management functionality.

This module provides unit tests for the NVMe device management system,
covering device discovery, operations, and NVMe over Fabrics (NVMeoF)
functionality. The tests are designed to validate the NVMe device interface
without requiring actual NVMe hardware.
"""

import json
from unittest.mock import MagicMock, patch

from sts.nvme import NvmeDevice


class TestNvmeDevice:
    """Test suite for NVMe device management."""

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_init(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test NVMe device initialization."""
        # Mock nvme list command with the exact data structure expected
        mock_result = MagicMock()
        mock_result.succeeded = True
        mock_result.stdout = json.dumps(
            {
                'Devices': [
                    {
                        'HostNQN': 'nqn.2014-08.org.nvmexpress:uuid:test-host',
                        'HostID': 'test-host-id',
                        'Subsystems': [
                            {
                                'Subsystem': 'nvme-subsys0',
                                'SubsystemNQN': 'nqn.2014-08.org.nvmexpress:uuid:test-subsystem',
                                'Controllers': [
                                    {
                                        'Controller': 'nvme0',
                                        'SerialNumber': 'TEST123',
                                        'ModelNumber': 'Test SSD',
                                        'Firmware': '1.0',
                                        'Transport': 'pcie',
                                        'Address': '0000:04:00.0',
                                        'Namespaces': [
                                            {
                                                'NSID': 1,
                                                'PhysicalSize': 250000000000,
                                                'SectorSize': 512,
                                                'UsedBytes': 100000000000,
                                                'MaximumLBA': 488281250,
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        )
        mock_run.return_value = mock_result

        # Test initialization
        device = NvmeDevice(name='nvme0n1')

        # Verify basic attributes (path will be Path object due to base class)
        assert device.name == 'nvme0n1'
        assert str(device.path) == '/dev/nvme0n1'
        assert device.controller == 'nvme0'

        # Verify discovered attributes
        assert device.serial == 'TEST123'
        assert device.model == 'Test SSD'
        assert device.firmware == '1.0'
        assert device.transport == 'pcie'
        assert device.address == '0000:04:00.0'
        assert device.nsid == 1
        assert device.physical_size == 250000000000
        assert device.sector_size == 512
        assert device.used_bytes == 100000000000
        assert device.maximum_lba == 488281250
        assert device.host_nqn == 'nqn.2014-08.org.nvmexpress:uuid:test-host'
        assert device.host_id == 'test-host-id'
        assert device.subsystem == 'nvme-subsys0'
        assert device.subsystem_nqn == 'nqn.2014-08.org.nvmexpress:uuid:test-subsystem'

    def test_init_package_install_failure(self) -> None:
        """Test initialization when package installation fails."""
        with (
            patch('sts.utils.packages.ensure_installed', return_value=False),
            patch('sts.utils.cmdline.run') as mock_run,
            patch('pathlib.Path.exists', return_value=True),
        ):
            mock_result = MagicMock()
            mock_result.succeeded = False
            mock_run.return_value = mock_result

            device = NvmeDevice(name='nvme0n1')
            # Should still initialize basic attributes
            assert device.name == 'nvme0n1'
            assert str(device.path) == '/dev/nvme0n1'
            assert device.controller == 'nvme0'

    @patch('sts.nvme.run')
    def test_has_nvme(self, mock_run: MagicMock) -> None:
        """Test checking if system has NVMe devices."""
        # Test with NVMe devices present
        mock_result = MagicMock()
        mock_result.failed = False
        mock_result.stdout = '/dev/nvme0n1     238.47  GB\n/dev/nvme1n1     500.00  GB'
        mock_run.return_value = mock_result

        assert NvmeDevice.has_nvme() is True
        mock_run.assert_called_with('nvme list')

        # Test with no NVMe devices
        mock_run.reset_mock()
        mock_result.stdout = 'No NVMe devices found'
        mock_run.return_value = mock_result

        assert NvmeDevice.has_nvme() is False

        # Test with command failure
        mock_run.reset_mock()
        mock_result.failed = True
        mock_run.return_value = mock_result

        assert NvmeDevice.has_nvme() is False

    @patch('sts.nvme.run')
    def test_get_all(self, mock_run: MagicMock) -> None:
        """Test getting all NVMe devices."""
        # Mock successful nvme list command
        mock_result = MagicMock()
        mock_result.failed = False
        mock_result.stdout = """/dev/nvme0n1     238.47  GB / 238.47  GB    512   B +  0 B
                            Samsung SSD 970 EVO 250GB               1.0
/dev/nvme1n1     500.00  GB / 500.00  GB    512   B +  0 B
                            Intel SSD 600P Series                   1.0"""
        mock_run.return_value = mock_result

        with patch.object(NvmeDevice, '__init__', return_value=None):
            devices = NvmeDevice.get_all()

            # Should find 2 devices
            assert len(devices) == 2
            mock_run.assert_called_with('nvme list')

        # Test with command failure
        mock_run.reset_mock()
        mock_result.failed = True
        mock_result.stderr = 'nvme command not found'
        mock_run.return_value = mock_result

        devices = NvmeDevice.get_all()
        assert len(devices) == 0

    def test_get_by_attribute(self) -> None:
        """Test getting devices by attribute value."""
        # Create mock devices
        device1 = NvmeDevice.__new__(NvmeDevice)
        device1.name = 'nvme0n1'
        device1.model = 'Samsung SSD 970 EVO'
        device1.transport = 'pcie'

        device2 = NvmeDevice.__new__(NvmeDevice)
        device2.name = 'nvme1n1'
        device2.model = 'Intel SSD 600P'
        device2.transport = 'pcie'

        with patch.object(NvmeDevice, 'get_all', return_value=[device1, device2]):
            # Test finding by model
            devices = NvmeDevice.get_by_attribute('model', 'Samsung SSD 970 EVO')
            assert len(devices) == 1
            assert devices[0].name == 'nvme0n1'

            # Test finding by transport (should return both)
            devices = NvmeDevice.get_by_attribute('transport', 'pcie')
            assert len(devices) == 2

            # Test finding non-existent attribute
            devices = NvmeDevice.get_by_attribute('nonexistent', 'value')
            assert len(devices) == 0

            # Test with empty parameters
            devices = NvmeDevice.get_by_attribute('', 'value')
            assert len(devices) == 0

            devices = NvmeDevice.get_by_attribute('model', '')
            assert len(devices) == 0

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_device_operations(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test basic device operations."""
        # Mock successful command result for all operations
        mock_result = MagicMock()
        mock_result.succeeded = True
        mock_result.failed = False
        mock_result.stdout = json.dumps({'Devices': []})
        mock_run.return_value = mock_result

        device = NvmeDevice(name='nvme0n1')

        # Test format operation
        assert device.format() is True

        # Test sanitize operation
        assert device.sanitize() is True

        # Test reset operation
        assert device.reset() is True

        # Test flush operation
        assert device.flush() is True

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.utils.cmdline.run')
    def test_device_operations_without_path(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test device operations when path is not available."""
        device = NvmeDevice(name='nvme0n1')
        device.path = None
        device.controller = None

        # Should fail when path is not available
        assert device.format() is False
        assert device.sanitize() is False
        assert device.reset() is False
        assert device.flush() is False

        # Should not call run command
        mock_run.assert_not_called()

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_get_smart_log(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test getting SMART log information."""
        # Mock for all operations - return smart data for get_smart_log calls
        smart_data = {
            'critical_warning': '0x0',
            'temperature': '35 C',
            'available_spare': '100%',
            'media_errors': '0',
            'num_err_log_entries': '0',
        }

        # Default result for device initialization
        init_result = MagicMock()
        init_result.succeeded = True
        init_result.failed = False
        init_result.stdout = json.dumps({'Devices': []})
        mock_run.return_value = init_result

        device = NvmeDevice(name='nvme0n1')

        # Now setup mock for SMART log operation
        smart_result = MagicMock()
        smart_result.failed = False
        smart_result.stdout = json.dumps(smart_data)
        mock_run.return_value = smart_result

        result = device.get_smart_log()
        assert result == smart_data

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.utils.cmdline.run')
    def test_get_smart_log_failure(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test SMART log retrieval failure."""
        # Mock command failure
        mock_result = MagicMock()
        mock_result.failed = True
        mock_result.stdout = ''
        mock_run.return_value = mock_result

        device = NvmeDevice(name='nvme0n1')
        result = device.get_smart_log()

        assert result == {}

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.utils.cmdline.run')
    def test_get_smart_log_invalid_json(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test SMART log with invalid JSON response."""
        mock_result = MagicMock()
        mock_result.failed = False
        mock_result.stdout = 'invalid json'
        mock_run.return_value = mock_result

        device = NvmeDevice(name='nvme0n1')
        result = device.get_smart_log()

        assert result == {}

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_nvmeof_operations(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test NVMe over Fabrics operations."""
        # Mock all nvme command calls to return successful results
        mock_result = MagicMock()
        mock_result.succeeded = True
        mock_result.failed = False
        mock_result.stdout = json.dumps({'Devices': []})
        mock_run.return_value = mock_result

        device = NvmeDevice(name='nvme0n1')
        device.host_nqn = 'nqn.2014-08.org.nvmexpress:uuid:test-host'

        # Test discover operation
        discover_result = MagicMock()
        discover_result.succeeded = True
        discover_result.failed = False
        discover_result.stdout = json.dumps({'discovered_subsystems': []})
        mock_run.return_value = discover_result

        result = device.discover(**{'--transport': 'tcp', '--traddr': '192.168.1.100'})
        assert result == {'discovered_subsystems': []}

        # Test connect operation
        connect_result = MagicMock()
        connect_result.succeeded = True
        mock_run.return_value = connect_result

        result = device.connect(**{'--transport': 'tcp', '--traddr': '192.168.1.100', '--nqn': 'nqn.test'})
        assert result is True

        # Test disconnect operation
        disconnect_result = MagicMock()
        disconnect_result.succeeded = True
        mock_run.return_value = disconnect_result

        result = device.disconnect('nqn.test')
        assert result is True

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_firmware_operations(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test firmware operations."""
        # Mock successful command results for all operations
        mock_result = MagicMock()
        mock_result.succeeded = True
        mock_result.failed = False
        mock_result.stdout = json.dumps({'Devices': []})
        mock_run.return_value = mock_result

        device = NvmeDevice(name='nvme0n1')

        # Test firmware download
        result = device.fw_download('/path/to/firmware.bin')
        assert result is True

        # Test firmware commit
        result = device.fw_commit('1', '1')
        assert result is True

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_feature_operations(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test feature get/set operations."""
        # Default result for device initialization
        init_result = MagicMock()
        init_result.succeeded = True
        init_result.failed = False
        init_result.stdout = json.dumps({'Devices': []})
        mock_run.return_value = init_result

        device = NvmeDevice(name='nvme0n1')

        # Test get feature
        feature_data = {'fid': 2, 'cdw11': 0, 'cdw12': 0}
        get_feature_result = MagicMock()
        get_feature_result.failed = False
        get_feature_result.stdout = json.dumps(feature_data)
        mock_run.return_value = get_feature_result

        result = device.get_feature('0x02')
        assert result == feature_data

        # Test set feature
        set_feature_result = MagicMock()
        set_feature_result.succeeded = True
        mock_run.return_value = set_feature_result

        result = device.set_feature('0x02', '0x00')
        assert result is True

    @patch('pathlib.Path.exists', return_value=True)
    @patch('sts.nvme.run')
    def test_self_test_operations(self, mock_run: MagicMock, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """Test self-test operations."""
        # Default result for device initialization
        init_result = MagicMock()
        init_result.succeeded = True
        init_result.failed = False
        init_result.stdout = json.dumps({'Devices': []})
        mock_run.return_value = init_result

        device = NvmeDevice(name='nvme0n1')

        # Test device self-test
        self_test_result = MagicMock()
        self_test_result.succeeded = True
        mock_run.return_value = self_test_result

        result = device.device_self_test('1')
        assert result is True

        # Test get self-test log
        test_log_data = {'current_operation': 0, 'completion': 0, 'result': []}
        get_log_result = MagicMock()
        get_log_result.failed = False
        get_log_result.stdout = json.dumps(test_log_data)
        mock_run.return_value = get_log_result

        result = device.get_self_test_log()
        assert result == test_log_data
