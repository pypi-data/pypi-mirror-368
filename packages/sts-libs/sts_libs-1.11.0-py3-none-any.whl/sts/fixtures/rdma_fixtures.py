# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""RDMA test fixtures.

This module provides fixtures for testing RDMA (Remote Direct Memory Access):
- Device discovery and validation
- Device configuration and management
- Port and interface handling
- SR-IOV configuration

Fixture Dependencies:
1. _exists_rdma (base fixture)
   - Validates RDMA device presence
   - Skips tests if no devices found

2. rdma_device (independent fixture)
   - Creates device factory function
   - Validates device existence
   - Provides device management

Common Usage:
1. Basic device validation:
   @pytest.mark.usefixtures('_exists_rdma')
   def test_rdma():
       # Test runs only if RDMA device exists

2. Specific device testing:
   def test_device(rdma_device):
       device = rdma_device('mlx5_0')
       # Test specific RDMA device

3. Port configuration:
   def test_ports(rdma_device):
       device = rdma_device('mlx5_0')
       ports = device.get_ports()
       # Test port configuration

4. SR-IOV setup:
   def test_sriov(rdma_device):
       device = rdma_device('mlx5_0')
       sriov = device.get_sriov()
       # Test SR-IOV configuration

Error Handling:
- Missing devices skip tests
- Invalid device IDs raise assertion errors
- Device access issues are logged
- Configuration failures are reported
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from sts.rdma import RdmaDevice, exists_device, exists_rdma

if TYPE_CHECKING:
    from collections.abc import Callable

    from sts.rdma import RdmaDevice as RdmaDeviceType


@pytest.fixture
def _exists_rdma() -> None:
    """Skip test if no RDMA device found.

    This fixture validates RDMA device presence:
    - Checks sysfs for RDMA devices
    - Skips test if no devices found
    - Logs available devices
    - Validates driver status

    Common device types:
    - Mellanox ConnectX (mlx4, mlx5)
    - Broadcom NetXtreme (bnxt_re)
    - Intel (i40iw)
    - Chelsio (cxgb4)

    Example:
        ```python
        @pytest.mark.usefixtures('_exists_rdma')
        def test_rdma():
            # Test runs only if RDMA device exists
            # Test is skipped if no devices found
        ```
    """
    if not exists_rdma():
        pytest.skip(reason='No RDMA device found')


@pytest.fixture(scope='class')
def rdma_device() -> Callable[[str], RdmaDeviceType]:
    """Create RDMA device factory.

    This fixture provides a factory function for RDMA devices:
    - Creates device instances on demand
    - Validates device existence
    - Provides device management interface
    - Supports multiple device types

    Device Management:
    - Port configuration
    - Interface binding
    - SR-IOV setup
    - Power management

    Returns:
        Factory function that takes HCA ID and returns RdmaDevice

    Example:
        ```python
        def test_rdma(rdma_device):
            # Create device instance
            device = rdma_device('mlx5_0')
        ...
            # Access device information
            assert device.exists
        ...
            # Configure ports
            ports = device.get_ports()
            for port in ports:
                print(f'Port {port.name}: {port.state}')
        ...
            # Set up SR-IOV if supported
            if device.is_sriov_capable:
                sriov = device.get_sriov()
                sriov.set_numvfs('4')
        ```
    """

    def _device_factory(hca_id: str) -> RdmaDeviceType:
        """Create RDMA device.

        Creates and validates RDMA device instance:
        - Checks device existence
        - Initializes device paths
        - Sets up device attributes
        - Validates configuration

        Args:
            hca_id: HCA ID (e.g. 'mlx5_0', 'mlx4_1')

        Returns:
            RDMA device instance

        Raises:
            AssertionError: If device not found or invalid

        Example:
            ```python
            device = _device_factory('mlx5_0')
            assert device.exists
            ```
        """
        assert exists_device(hca_id), f'No RDMA device found: {hca_id}'
        return RdmaDevice(ibdev=hca_id)

    return _device_factory
