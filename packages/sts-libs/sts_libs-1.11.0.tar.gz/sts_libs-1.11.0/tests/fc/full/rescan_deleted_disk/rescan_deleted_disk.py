# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""FC device discovery and rescan functionality tests.

This module tests FC device capabilities:
1. Driver information discovery
2. PCI host information
3. Device deletion and rescan recovery
"""

import logging
from pathlib import Path

import pytest

from sts.fc import FcDevice
from sts.utils.cmdline import run
from sts.utils.errors import DeviceNotFoundError
from sts.utils.modules import ModuleInfo
from sts.utils.packages import ensure_installed


class TestFcDevice:
    """Test Fibre Channel device functionality.

    Tests:
    - Driver information retrieval
    - PCI host details
    - Device deletion and recovery via rescan
    """

    @pytest.fixture(autouse=True)
    def _device(self, get_fc_device: FcDevice) -> None:
        """Set up FC device for testing.

        Args:
            get_fc_device: Fixture providing an FcDevice instance

        Attributes:
            device: FC device under test
        """
        self.device = get_fc_device
        # Validate device setup
        assert self.device.path, 'Device path is empty'
        assert Path(self.device.path).exists(), f'Device path {self.device.path} does not exist'
        assert self.device.host_id, 'No host ID found'

    def test_show_driver_info(self) -> None:
        """Verify FC driver information can be retrieved."""
        if not self.device.driver:
            pytest.skip(f'No driver found for device {self.device}')

        mod_info = ModuleInfo.from_name(self.device.driver)
        assert mod_info, f'Failed to get module info for {self.device.driver}'
        logging.info('Driver info: %s', mod_info)

    def test_lspci_fc_host(self) -> None:
        """Verify PCI information for FC host can be displayed."""
        if not self.device.pci_id:
            pytest.skip(f'No PCI ID found for device {self.device}')

        assert ensure_installed('pciutils'), 'pciutils package required'
        result = run(f'lspci -s {self.device.pci_id} -vvv')
        assert result.succeeded, f'lspci command failed: {result.stderr}'
        logging.info('PCI info:\n%s', result.stdout)

    def test_delete_disk_then_rescan_host(self) -> None:
        """Verify disk can be deleted and recovered via host rescan."""
        # Initial state validation
        logging.info('Verifying initial device state: %s', self.device.path)
        assert self.device.check_sector_zero(), f'Initial I/O check failed for {self.device.path}'

        # Delete disk
        logging.info('Deleting disk: %s', self.device.path)
        assert self.device.delete_disk(), f'Failed to delete {self.device.path}'

        # Rescan host
        logging.info('Rescanning host%s', self.device.host_id)
        assert self.device.rescan_host(), f'Host {self.device.host_id} rescan failed'

        # Wait for udev to process changes
        self.device.wait_udev()

        # Verify device recovery
        logging.info('Verifying device recovery: %s', self.device.path)
        try:
            self.device.validate_device_exists()
        except DeviceNotFoundError:
            pytest.fail(f'Device {self.device.path} did not reappear after rescan')

        # Verify I/O after recovery
        assert self.device.check_sector_zero(), f'Post-rescan I/O check failed for {self.device.path}'
        logging.info('Device successfully recovered and verified: %s', self.device.path)
