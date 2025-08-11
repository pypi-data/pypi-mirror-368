# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSCSI test fixtures.

This module provides fixtures for testing iSCSI:
- Package installation
- Service management
- Device configuration
- Parameter verification
- Session management

Fixture Dependencies:
1. _iscsi_test (base fixture)
   - Installs iSCSI utilities
   - Manages sessions
2. iscsi_localhost_test (depends on _iscsi_test)
   - Sets up target environment
3. iscsi_target (depends on iscsi_localhost_test)
   - Creates target and initiator
   - Manages connections
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest

from sts.iscsi.config import IscsiNode, set_initiatorname
from sts.iscsi.iscsiadm import IscsiAdm
from sts.multipath import MultipathDevice, MultipathService
from sts.scsi import ScsiDevice
from sts.target import BackstoreFileio, Iscsi, IscsiLUN, create_basic_iscsi_target
from sts.utils.packages import ensure_installed
from sts.utils.system import SystemManager

ISCSID_SERVICE_NAME = 'iscsid'


@dataclass
class IscsiTestConfig:
    """Configuration for iSCSI test environment.

    Attributes:
        base_iqn: Base IQN for test
        target_iqn: Target IQN
        initiator_iqn: Initiator IQN
        size: Size of LUNs
        n_luns: Number of LUNs
    """

    base_iqn: str
    target_iqn: str
    initiator_iqn: str
    size: str = '1G'
    n_luns: int = 1


def generate_test_iqns(test_name: str) -> tuple[str, str, str]:
    """Generate IQNs for test environment.

    Args:
        test_name: Name of the test

    Returns:
        Tuple of (base_iqn, target_iqn, initiator_iqn)
    """
    test_name = test_name.split('[')[0]  # Remove parametrize part
    # Replace underscores with dashes for IQN compatibility
    test_name = test_name.replace('_', '-')
    base_iqn = f'iqn.2024-01.sts.{test_name}'
    target_iqn = f'{base_iqn}:target'
    initiator_iqn = f'{base_iqn}:initiator'
    return base_iqn, target_iqn, initiator_iqn


@contextmanager
def manage_iscsi_session(node: IscsiNode) -> Generator[None, None, None]:
    """Context manager for iSCSI session management.

    Args:
        node: IscsiNode instance to manage

    Yields:
        None
    """
    try:
        yield
    finally:
        node.logout()


@pytest.fixture(scope='class')
def _iscsi_test() -> Generator[None, None, None]:
    """Base fixture for iSCSI testing.

    This fixture provides the foundation for iSCSI tests:
    - Installs required packages
    - Logs system information
    - Manages session cleanup

    Used by:
    - iscsi_localhost_test fixture
    - Other iSCSI test fixtures

    Example:
        ```python
        @pytest.mark.usefixtures('_iscsi_test')
        def test_iscsi():
            # iSCSI utilities are installed
            # Sessions are cleaned up after test
        ```
    """
    system = SystemManager()
    assert ensure_installed('iscsi-initiator-utils')
    logging.info(f'Kernel version: {system.info.kernel}')

    # Clean up existing sessions
    iscsiadm = IscsiAdm()
    iscsiadm.node_logoutall()

    yield

    # Clean up sessions
    iscsiadm.node_logoutall()


@pytest.fixture(scope='class')
def iscsi_localhost_test(request: pytest.FixtureRequest, _iscsi_test: None) -> Generator[str, None, None]:
    """Set up iSCSI target environment.

    This fixture:
    - Installs target utilities
    - Creates target configuration
    - Cleans up environment

    Args:
        request: Fixture request
        _iscsi_test: Parent fixture providing base setup

    Yields:
        Target IQN

    Example:
        ```python
        def test_target(iscsi_localhost_test):
            target_iqn = iscsi_localhost_test
            assert Iscsi(target_iqn).exists()
        ```
    """
    assert ensure_installed('targetcli')

    # Generate IQNs
    _, target_iqn, _ = generate_test_iqns(request.node.name)

    # Clean up target config
    target = Iscsi(target_wwn=target_iqn)
    target.delete_target()

    yield target_iqn

    # Clean up target config
    target.delete_target()


@pytest.fixture
def get_test_device() -> Callable[[], Path]:
    """Get test device path.

    Returns:
        Function to get device path

    Example:
        ```python
        def test_device(get_test_device):
            device = get_test_device()
            assert device.exists()
        ```
    """

    def _get_test_device() -> Path:
        """Get test device path.

        Returns:
            Device path

        Raises:
            AssertionError: If no device found
        """
        mp_service = MultipathService()
        if mp_service.is_running():
            devices = MultipathDevice.get_all()
            if devices and devices[0].path:
                return Path(str(devices[0].path))

        devices = ScsiDevice.get_by_vendor('LIO-ORG')
        # Break down complex assertion
        assert devices, 'No LIO devices found'
        assert devices[0].path, 'Device path not available'
        return Path(str(devices[0].path))

    return _get_test_device


@pytest.fixture
def iscsi_target(request: pytest.FixtureRequest, iscsi_localhost_test: None) -> Generator[IscsiNode, None, None]:  # noqa: ARG001
    """Create iSCSI target and connect initiator.

    This fixture:
    - Creates target with specified size and number of LUNs
    - Sets up initiator
    - Logs in to target
    - Yields connected node
    - Cleans up on exit

    Args:
        request: Fixture request with parameters:
            - size: Size of each LUN (default: '1G')
            - n_luns: Number of LUNs (default: 1)
        iscsi_localhost_test: Parent fixture providing target IQN

    Example:
        ```python
        @pytest.mark.parametrize('iscsi_target', [{'size': '2G', 'n_luns': 2}], indirect=True)
        def test_something(iscsi_target):
            assert iscsi_target.exists()
        ```
    """
    # Generate IQNs
    _, target_iqn, initiator_iqn = generate_test_iqns(request.node.name)

    # Get parameters
    params = request.param if hasattr(request, 'param') else {}
    config = IscsiTestConfig(
        base_iqn=target_iqn.rsplit(':', 1)[0],
        target_iqn=target_iqn,
        initiator_iqn=initiator_iqn,
        size=params.get('size', '1G'),
        n_luns=params.get('n_luns', 1),
    )

    # Set initiator name
    assert set_initiatorname(config.initiator_iqn), 'Failed to set initiator name'

    # Create target
    assert create_basic_iscsi_target(
        target_wwn=config.target_iqn,
        initiator_wwn=config.initiator_iqn,
        size=config.size,
    ), 'Failed to create target'

    # Create additional LUNs if needed
    if config.n_luns > 1:
        test_name = request.node.name.split('[')[0]
        for i in range(1, config.n_luns):
            backstore_name = f'{test_name}_lun{i}'
            backstore = BackstoreFileio(name=backstore_name)
            backstore.create_backstore(size=config.size, file_or_dev=f'{backstore_name}_file')
            IscsiLUN(target_wwn=config.target_iqn).create_lun(storage_object=backstore.path)

    # Set up initiator and login
    node = IscsiNode.setup_and_login(
        portal='127.0.0.1:3260',
        initiator_iqn=config.initiator_iqn,
        target_iqn=config.target_iqn,
    )

    with manage_iscsi_session(node):
        yield node
