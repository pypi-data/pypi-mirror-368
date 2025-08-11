# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Target test fixtures.

This module provides fixtures for testing storage targets:
- Target creation and configuration
- Backstore management (block, fileio, ramdisk)
- ACL and authentication setup
- LUN management

Fixture Dependencies:
1. _target_test (base fixture)
   - Installs target utilities
   - Manages target cleanup
   - Logs system information

2. backstore_*_setup (depends on _target_test)
   - block: Creates block backstore with loop device
   - fileio: Creates fileio backstore
   - ramdisk: Creates ramdisk backstore

3. iscsi_target_setup (depends on _target_test)
   - Creates iSCSI target
   - Configures ACLs and LUNs
   - Manages cleanup

4. configure_auth (depends on _target_test)
   - Sets up CHAP authentication
   - Configures mutual CHAP
   - Manages credentials

5. loopback_devices
   - Creates loopback devices for testing
   - Supports custom block size and device count
   - Manages device cleanup automatically
   - Yields list of BlockDevice instances

Common Usage:
1. Basic target testing:
   @pytest.mark.usefixtures('_target_test')
   def test_target():
       # Create and test targets
       # Targets are cleaned up after test

2. Backstore testing:
   @pytest.mark.parametrize('backstore_block_setup',
                           [{'name': 'test', 'size': 1024*1024}],
                           indirect=True)
   def test_backstore(backstore_block_setup):
       # Test backstore operations

3. iSCSI target testing:
   @pytest.mark.parametrize('iscsi_target_setup',
                           [{'t_iqn': 'iqn.test', 'n_luns': 2}],
                           indirect=True)
   def test_iscsi(iscsi_target_setup):
       # Test iSCSI target operations

4. Authentication testing:
   @pytest.mark.parametrize('configure_auth',
                           [{'t_iqn': 'iqn.test',
                             'chap_username': 'user',
                             'chap_password': 'pass'}],
                           indirect=True)
   def test_auth(configure_auth):
       # Test authentication

5. Loopback device testing:
   # Using test parametrization
   @pytest.mark.parametrize('block_size', [512, 1024])
   def test_loopback(loopback_devices):
       # Uses block_size from parametrize, device_count=2 (default)

   # Using fixture parametrization
   @pytest.mark.parametrize('loopback_devices',
                           [{'device_count': 4, 'block_size': 1024}],
                           indirect=True)
   def test_loopback_custom(loopback_devices):
       # Uses custom device_count and block_size
       # Devices are automatically cleaned up

Error Handling:
- Package installation failures fail test
- Target creation failures are handled
- Resource cleanup runs on failure
- Authentication errors are logged
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from sts.loop import LoopDevice
from sts.target import (
    ACL,
    BackstoreBlock,
    BackstoreFileio,
    BackstoreRamdisk,
    Iscsi,
    IscsiLUN,
    Targetcli,
    cleanup_loopback_devices,
    create_loopback_devices,
)
from sts.utils.packages import ensure_installed, log_package_versions

if TYPE_CHECKING:
    from collections.abc import Generator

    from sts.blockdevice import BlockDevice

# Constants
DEFAULT_TARGET_IQN = 'iqn.2003-01.com.redhat:targetauthtest'


@pytest.fixture(scope='class')
def _target_test() -> Generator[None, None, None]:
    """Install target utils and clean up before/after test.

    This fixture provides the foundation for target testing:
    - Installs targetcli package
    - Logs system information
    - Cleans up target configuration
    - Ensures consistent environment

    Package Installation:
    - targetcli: Target configuration tool
    - Required kernel modules
    - System dependencies

    Target Cleanup:
    1. Removes test target before test
    2. Removes test target after test
    3. Handles force cleanup if needed

    Example:
        ```python
        @pytest.mark.usefixtures('_target_test')
        def test_target():
            # Create and test targets
            # Configuration is cleaned up after test
        ```
    """
    assert ensure_installed('targetcli')
    packages = ['kernel', 'targetcli', 'target-restore', 'python3-rtslib', 'python3-configshell']
    log_package_versions(*packages)

    targetcli = Targetcli(path='/')
    # Clear target config before the test
    targetcli.clearconfig()

    yield

    # Clear target config after the test
    targetcli.clearconfig()


@pytest.fixture
def backstore_block_setup(_target_test: None, request: pytest.FixtureRequest) -> Generator[BackstoreBlock, None, None]:
    """Create block backstore with loop device.

    Creates block backstore using loop device:
    - Creates temporary loop device
    - Sets up block backstore
    - Manages cleanup
    - Supports custom size

    Args:
        request: Fixture request with parameters:
            - name: Backstore name
            - size: Loop device size in MB

    Example:
        ```python
        @pytest.mark.parametrize('backstore_block_setup', [{'name': 'test', 'size': 1024}], indirect=True)
        def test_backstore(backstore_block_setup):
            assert backstore_block_setup.exists
        ```
    """
    loop_dev = None
    backstore = None
    try:
        # Create loop device
        loop_dev = LoopDevice.create(
            name=request.param['name'],
            size_mb=request.param['size'] // (1024 * 1024),
        )
        if not loop_dev:
            pytest.skip('Failed to create loop device')

        # Create backstore
        backstore = BackstoreBlock(name=request.param['name'])
        backstore.create_backstore(dev=str(loop_dev.path))
        yield backstore

    except Exception:
        logging.exception('Failed to set up block backstore')
        raise

    finally:
        # Clean up
        if backstore:
            backstore.delete_backstore()
        if loop_dev:
            loop_dev.remove()


@pytest.fixture
def backstore_fileio_setup(
    _target_test: None, request: pytest.FixtureRequest
) -> Generator[BackstoreFileio, None, None]:
    """Create fileio backstore.

    Creates fileio backstore:
    - Creates backing file
    - Sets up fileio backstore
    - Manages cleanup
    - Supports custom size

    Args:
        request: Fixture request with parameters:
            - name: Backstore name
            - size: File size in bytes
            - file_or_dev: File path

    Example:
        ```python
        @pytest.mark.parametrize('backstore_fileio_setup', [{'name': 'test', 'size': 1024 * 1024}], indirect=True)
        def test_backstore(backstore_fileio_setup):
            assert backstore_fileio_setup.exists
        ```
    """
    backstore = None
    try:
        backstore = BackstoreFileio(name=request.param['name'])
        backstore.create_backstore(
            size=str(request.param['size']),
            file_or_dev=request.param.get('file_or_dev') or f'{request.param["name"]}_file',
        )
        yield backstore

    except Exception:
        logging.exception('Failed to set up fileio backstore')
        raise

    finally:
        if backstore:
            backstore.delete_backstore()


@pytest.fixture
def backstore_ramdisk_setup(
    _target_test: None, request: pytest.FixtureRequest
) -> Generator[BackstoreRamdisk, None, None]:
    """Create ramdisk backstore.

    Creates ramdisk backstore:
    - Allocates memory
    - Sets up ramdisk backstore
    - Manages cleanup
    - Supports custom size

    Args:
        request: Fixture request with parameters:
            - name: Backstore name
            - size: Size in bytes

    Example:
        ```python
        @pytest.mark.parametrize('backstore_ramdisk_setup', [{'name': 'test', 'size': 1024 * 1024}], indirect=True)
        def test_backstore(backstore_ramdisk_setup):
            assert backstore_ramdisk_setup.exists
        ```
    """
    backstore = None
    try:
        backstore = BackstoreRamdisk(name=request.param['name'])
        backstore.create_backstore(size=str(request.param['size']))
        yield backstore

    except Exception:
        logging.exception('Failed to set up ramdisk backstore')
        raise

    finally:
        if backstore:
            backstore.delete_backstore()


@contextmanager
def target_setup(
    *,
    t_iqn: str | None = None,
    i_iqn: str | None = None,
    n_luns: int = 0,
    back_size: int | None = None,
) -> Generator[Iscsi, None, None]:
    """Set up iSCSI target.

    Creates and manages iSCSI target:
    - Creates target with IQN
    - Sets up ACLs if needed
    - Creates LUNs if needed
    - Manages cleanup

    Args:
        t_iqn: Target IQN
        i_iqn: Initiator IQN
        n_luns: Number of LUNs
        back_size: Backstore size in bytes

    Yields:
        iSCSI target instance

    Example:
        ```python
        with target_setup(t_iqn='iqn.test', n_luns=2) as target:
            # Use target
            assert target.exists
        ```
    """
    target_wwn = t_iqn or DEFAULT_TARGET_IQN
    target = Iscsi(target_wwn=target_wwn)

    try:
        # Create target
        target.create_target()

        # Add ACL if needed
        if i_iqn:
            acl = ACL(target_wwn=target_wwn, initiator_wwn=i_iqn)
            acl.create_acl()

        # Add LUNs if needed
        if back_size and n_luns > 0:
            luns = IscsiLUN(target_wwn)
            for n in range(n_luns):
                name = f'backstore{n}'
                backstore = BackstoreFileio(name=name)
                backstore.create_backstore(size=str(back_size), file_or_dev=f'{name}_file')
                luns.create_lun(storage_object=backstore.path)

        yield target

    finally:
        target.delete_target()
        # Clean up backstore files
        for n in range(n_luns):
            Path(f'backstore{n}_file').unlink(missing_ok=True)


@pytest.fixture(scope='class')
def iscsi_target_setup(_target_test: None, request: pytest.FixtureRequest) -> Generator[Iscsi, None, None]:
    """Create iSCSI target with ACLs and LUNs.

    Creates complete iSCSI target:
    - Creates target with IQN
    - Sets up ACLs
    - Creates LUNs
    - Manages cleanup

    Args:
        request: Fixture request with parameters:
            - t_iqn: Target IQN (optional)
            - i_iqn: Initiator IQN (optional)
            - n_luns: Number of LUNs (optional)
            - back_size: Backstore size in bytes (optional)

    Example:
        ```python
        @pytest.mark.parametrize('iscsi_target_setup', [{'t_iqn': 'iqn.test', 'n_luns': 2}], indirect=True)
        def test_target(iscsi_target_setup):
            assert iscsi_target_setup.exists
        ```
    """
    params = request.param
    with target_setup(
        t_iqn=params.get('t_iqn'),
        i_iqn=params.get('i_iqn'),
        n_luns=params.get('n_luns', 0),
        back_size=params.get('back_size'),
    ) as target:
        yield target


@pytest.fixture
def configure_auth(request: pytest.FixtureRequest) -> Generator[Iscsi, None, None]:
    """Configure CHAP authentication.

    Sets up CHAP authentication:
    - Creates target with auth
    - Configures CHAP credentials
    - Supports mutual CHAP
    - Manages cleanup

    Args:
        request: Fixture request with parameters:
            - t_iqn: Target IQN
            - i_iqn: Initiator IQN
            - chap_username: CHAP username
            - chap_password: CHAP password
            - chap_target_username: Mutual CHAP username (optional)
            - chap_target_password: Mutual CHAP password (optional)
            - tpg_or_acl: Configure TPG or ACL auth

    Example:
        ```python
        @pytest.mark.parametrize(
            'configure_auth', [{'t_iqn': 'iqn.test', 'chap_username': 'user', 'chap_password': 'pass'}], indirect=True
        )
        def test_auth(configure_auth):
            assert configure_auth.exists
        ```
    """
    target_wwn = request.param['t_iqn']
    target = Iscsi(target_wwn=target_wwn)

    try:
        # Create target
        target.create_target()

        # Add backstore
        backstore = BackstoreFileio(name='auth_test')
        backstore.create_backstore(size='1M', file_or_dev='auth_test_file')
        luns = IscsiLUN(target_wwn=target_wwn)
        luns.create_lun(storage_object=backstore.path)

        # Configure auth
        if request.param['tpg_or_acl'] == 'acl':
            acl = ACL(target_wwn=target_wwn, initiator_wwn=request.param['i_iqn'])
            acl.create_acl()
            acl.set_auth(
                userid=request.param['chap_username'],
                password=request.param['chap_password'],
                mutual_userid=request.param.get('chap_target_username', ''),
                mutual_password=request.param.get('chap_target_password', ''),
            )

        yield target

    finally:
        target.delete_target()


@pytest.fixture
def loopback_devices(request: pytest.FixtureRequest) -> Generator[list[BlockDevice], None, None]:
    """Create loopback devices for testing.

    This fixture creates loopback devices with the specified block size
    from the parametrized test, yields them for testing, and ensures
    proper cleanup afterward.

    Parameters (from test parametrization or fixture params):
        block_size: Block size for devices (default: 512)
        device_count: Number of devices to create (default: 2)

    Yields:
        List of BlockDevice instances representing the created loopback devices

    Example:
        ```python
        # Using test parametrization
        @pytest.mark.parametrize('block_size', [512, 1024])
        def test_loopback(loopback_devices):
            # Uses block_size from parametrize, device_count=2 (default)

        # Using fixture parametrization
        @pytest.mark.parametrize('loopback_devices', [{'device_count': 4, 'block_size': 1024}], indirect=True)
        def test_loopback(loopback_devices):
            # Uses custom device_count and block_size
        ```
    """
    # Get parameters with defaults
    if hasattr(request, 'param') and isinstance(request.param, dict):
        # Fixture is parametrized with dict
        device_count = request.param.get('device_count', 2)
        block_size = request.param.get('block_size', 512)
    else:
        # Get from test parametrization or use defaults
        device_count = getattr(request.node.callspec, 'params', {}).get('device_count', 2)
        block_size = getattr(request.node.callspec, 'params', {}).get('block_size', 512)

    # Create devices
    devices = create_loopback_devices(device_count, block_size=block_size)

    try:
        yield devices
    finally:
        # Clean up
        cleanup_loopback_devices(devices)
