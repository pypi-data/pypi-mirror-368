# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Stratis test fixtures.

This module provides fixtures for testing Stratis storage:
- Pool creation and management
- Filesystem operations
- Encryption configuration
- Error injection and recovery

Fixture Dependencies:
1. _stratis_test (base fixture)
   - Installs Stratis packages
   - Manages pool cleanup
   - Logs system information

2. setup_stratis_key (independent fixture)
   - Creates encryption key
   - Manages key registration
   - Handles key cleanup

3. stratis_test_pool (depends on loop_devices)
   - Creates test pool
   - Manages devices
   - Handles cleanup

4. stratis_encrypted_pool (depends on loop_devices, setup_stratis_key)
   - Creates encrypted pool
   - Manages key and devices
   - Handles secure cleanup

5. stratis_failing_pool (depends on scsi_debug_devices)
   - Creates pool with failing device
   - Injects failures
   - Tests error handling

Common Usage:
1. Basic pool testing:
   @pytest.mark.usefixtures('_stratis_test')
   def test_stratis():
       # Create and test pools
       # Pools are cleaned up after test

2. Encrypted pool testing:
   def test_encryption(stratis_encrypted_pool):
       assert stratis_encrypted_pool.is_encrypted
       # Test encrypted operations

3. Error handling testing:
   def test_failures(stratis_failing_pool):
       assert not stratis_failing_pool.stop()
       # Test failure handling

Error Handling:
- Package installation failures fail test
- Pool creation failures skip test
- Device failures are handled gracefully
- Resources are cleaned up on failure
"""

import logging
from collections.abc import Generator
from os import getenv
from pathlib import Path

import pytest

from sts.lvm import LogicalVolume, PhysicalVolume, VolumeGroup
from sts.scsi_debug import ScsiDebugDevice
from sts.stratis.base import Key
from sts.stratis.pool import PoolCreateConfig, StratisPool
from sts.utils.cmdline import run
from sts.utils.packages import ensure_installed
from sts.utils.system import SystemInfo, SystemManager


@pytest.fixture(scope='class')
def _stratis_test() -> Generator[None, None, None]:
    """Install Stratis packages and clean up before/after test.

    This fixture provides the foundation for Stratis testing:
    - Installs required packages
    - Logs system information
    - Manages pool cleanup
    - Ensures consistent environment

    Package Installation:
    - stratis-cli: Command line interface
    - stratisd: Daemon service
    - Required dependencies

    Pool Cleanup:
    1. Removes test pools before test
    2. Removes test pools after test
    3. Handles force cleanup if needed
    4. Only affects pools with test prefix

    System Information:
    - Kernel version
    - Stratis version
    - System configuration
    """
    system = SystemManager()
    assert ensure_installed('stratis-cli', 'stratisd')

    # Log system information
    system.info.log_all()
    logging.info(run('stratis --version').stdout.rstrip())

    # Clean up before test
    if system.is_service_running('stratisd'):
        pools = StratisPool.get_all()
        for pool in pools:
            if pool.name and pool.name.startswith('sts-stratis-test-'):
                pool.destroy()

    yield

    # Clean up after test
    pools = StratisPool.get_all()
    for pool in pools:
        if pool.name and pool.name.startswith('sts-stratis-test-'):
            pool.destroy()


@pytest.fixture
def setup_stratis_key() -> Generator[str, None, None]:
    """Set up Stratis encryption key.

    Creates and manages encryption key:
    - Creates temporary key file
    - Registers key with Stratis
    - Handles key cleanup
    - Supports custom key configuration

    Configuration (via environment):
    - STRATIS_KEY_DESC: Key description (default: 'sts-stratis-test-key')
    - STRATIS_KEY_PATH: Key file path (default: '/tmp/sts-stratis-test-key')
    - STRATIS_KEY: Key content (default: 'Stra123tisKey45')

    Key Management:
    1. Creates key file with specified content
    2. Registers key with Stratis daemon
    3. Yields key description for use
    4. Unregisters key and removes file

    Example:
        ```python
        def test_encryption(setup_stratis_key):
            # Create encrypted pool
            pool = StratisPool()
            pool.create(key_desc=setup_stratis_key)
            assert pool.is_encrypted
        ```
    """
    stratis_key = Key()
    keydesc = getenv('STRATIS_KEY_DESC', 'sts-stratis-test-key')
    keypath = getenv('STRATIS_KEY_PATH', '/tmp/sts-stratis-test-key')
    key = getenv('STRATIS_KEY', 'Stra123tisKey45')

    # Create key file
    keyp = Path(keypath)
    keyp.write_text(key)
    assert keyp.is_file()

    # Register key with Stratis
    assert stratis_key.set(keydesc=keydesc, keyfile_path=keypath).succeeded

    yield keydesc

    # Clean up
    assert stratis_key.unset(keydesc).succeeded
    keyp.unlink()
    assert not keyp.is_file()


@pytest.fixture
def stratis_clevis_test() -> Generator[dict[str, str], None, None]:
    """Set up Tang server for Stratis Clevis encryption testing.

    This fixture configures the Tang server environment:
    - Ensures Tang server packages are installed
    - Starts Tang service
    - Gets server information for encryption
    - Handles cleanup

    Package Installation:
    - tang: Tang server package
    - curl: For HTTP requests
    - jose: For JWK operations
    - jq: For JSON processing

    Service Management:
    1. Installs required packages
    2. Starts Tang service
    3. Gets server thumbprint
    4. Cleans up after tests

    Returns:
        Dictionary containing:
        - thumbprint: Server thumbprint for verification
        - url: Tang server URL

    Example:
        ```python
        def test_tang(stratis_clevis_test):
            # Create encrypted pool with Tang
            config = PoolCreateConfig(
                clevis='tang', tang_url=stratis_clevis_test['url'], thumbprint=stratis_clevis_test['thumbprint']
            )
        ```
    """
    system = SystemManager()
    system_info = SystemInfo()
    tang_service = 'tangd.socket'

    # Install required packages
    required_packages = ['tang', 'curl', 'jose', 'jq', 'coreutils']
    assert ensure_installed(*required_packages), 'Failed to install required packages'

    # Start Tang service if not running
    if not system.is_service_running(tang_service):
        assert system.service_start(tang_service), f'Failed to start {tang_service}'

    # Get server thumbprint
    cmd = (
        f'curl -s {system_info.hostname}/adv | '
        f'jq -r .payload | '
        f'base64 -d | '
        f'jose jwk use -i- -r -u verify -o- | '
        f'jose jwk thp -i-'
    )
    result = run(cmd=cmd)
    assert result.succeeded, 'Failed to get Tang server thumbprint'
    assert result.stdout.strip(), 'Empty thumbprint received'

    # Prepare server information
    clevis_info = {'thumbprint': result.stdout.strip(), 'url': f'http://{system_info.hostname}'}

    yield clevis_info

    # Clean up
    if system.is_service_running(tang_service):
        assert system.service_stop(tang_service), f'Failed to stop {tang_service}'


@pytest.fixture
def stratis_test_pool(loop_devices: list[str]) -> Generator[StratisPool, None, None]:
    """Create test pool with loop devices.

    Creates and manages test pool:
    - Uses loop devices as storage
    - Creates standard pool
    - Handles cleanup
    - Supports testing operations

    Args:
        loop_devices: Loop device fixture (requires 2 devices)

    Pool Configuration:
    - Name: 'sts-stratis-test-pool'
    - Devices: Provided loop devices
    - Standard (non-encrypted) pool
    - Default settings

    Example:
        ```python
        @pytest.mark.parametrize('loop_devices', [2], indirect=True)
        def test_pool(stratis_test_pool):
            # Test pool operations
            fs = stratis_test_pool.create_filesystem('test')
            assert fs.exists
        ```
    """
    pool = StratisPool()
    pool.name = 'sts-stratis-test-pool'
    pool.blockdevs = loop_devices

    # Create pool
    if not pool.create():
        pytest.skip('Failed to create test pool')

    yield pool

    # Clean up
    pool.destroy()


@pytest.fixture
def stratis_encrypted_pool(loop_devices: list[str], setup_stratis_key: str) -> Generator[StratisPool, None, None]:
    """Create encrypted test pool with loop devices.

    Creates and manages encrypted pool:
    - Uses loop devices as storage
    - Creates encrypted pool
    - Manages encryption key
    - Handles secure cleanup

    Args:
        loop_devices: Loop device fixture (requires 2 devices)
        setup_stratis_key: Stratis key fixture

    Pool Configuration:
    - Name: 'sts-stratis-test-pool'
    - Devices: Provided loop devices
    - Encrypted with provided key
    - Default settings

    Example:
        ```python
        @pytest.mark.parametrize('loop_devices', [2], indirect=True)
        def test_pool(stratis_encrypted_pool):
            # Test encrypted operations
            assert stratis_encrypted_pool.is_encrypted
            fs = stratis_encrypted_pool.create_filesystem('test')
            assert fs.exists
        ```
    """
    pool = StratisPool()
    pool.name = 'sts-stratis-test-pool'
    pool.blockdevs = loop_devices

    # Create encrypted pool
    config = PoolCreateConfig(key_desc=setup_stratis_key)
    if not pool.create(config):
        pytest.skip('Failed to create encrypted test pool')

    yield pool

    # Clean up
    pool.destroy()


@pytest.fixture
def stratis_key_desc_pool(loop_devices: list[str], setup_stratis_key: str) -> Generator[StratisPool, None, None]:
    """Create a pool with keyring encryption."""
    pool = StratisPool()
    pool.name = 'sts-stratis-test-pool'
    pool.blockdevs = loop_devices[:2]  # Use first two devices initially
    config = PoolCreateConfig(key_desc=setup_stratis_key)
    assert pool.create(config)
    yield pool
    pool.destroy()


@pytest.fixture
def stratis_tang_pool(
    loop_devices: list[str], stratis_clevis_test: dict[str, str]
) -> Generator[StratisPool, None, None]:
    """Create a pool with Tang encryption."""
    pool = StratisPool()
    pool.name = 'sts-stratis-test-pool'
    pool.blockdevs = loop_devices[:2]  # Use first two devices initially
    config = PoolCreateConfig(
        clevis='tang', tang_url=stratis_clevis_test['url'], thumbprint=stratis_clevis_test['thumbprint']
    )
    assert pool.create(config)
    yield pool
    pool.destroy()


@pytest.fixture
def stratis_extend_lvm(
    _lvm_test: None,
    loop_devices: list[str],
) -> Generator[LogicalVolume, None, None]:
    """Create a logical volume 70%vg size which we will use to test stratis extend-data.

    First two devices from loop_devices are used for creating stratis pool.
    This fixture will use third and fourth loop device as PV.
    """
    vg_name = getenv('STRATIS_VG_NAME', 'sts-stratis-volume-group')
    lv_name = getenv('STRATIS_LV_NAME', 'sts-stratis-logical-volume')
    pvs = []
    assert len(loop_devices) > 4, 'Not enough loop devices is available'
    devices = loop_devices[2:4]
    try:
        # Create PVs
        for device in devices:
            pv = PhysicalVolume(name=device, path=device)
            assert pv.create(), f'Failed to create PV on device {device}'
            pvs.append(pv)

        # Create VG
        vg = VolumeGroup(name=vg_name, pvs=devices)
        assert vg.create(), f'Failed to create VG {vg_name}'
        lv = LogicalVolume(name=lv_name, vg=vg_name)
        assert lv.create(extents='70%vg')
        yield lv

    finally:
        # Cleanup in reverse order
        vg = VolumeGroup(name=vg_name)
        if not vg.remove():
            logging.warning(f'Failed to remove VG {vg_name}')

        for pv in pvs:
            if not pv.remove():
                logging.warning(f'Failed to remove PV {pv.path}')


@pytest.fixture
def stratis_no_enc_pool(loop_devices: list[str]) -> Generator[StratisPool, None, None]:
    """Create a pool without encryption."""
    pool = StratisPool()
    pool.name = 'sts-stratis-test-pool'
    pool.blockdevs = loop_devices[:2]  # Use first two devices initially
    assert pool.create()
    yield pool
    pool.destroy()


@pytest.fixture
def stratis_failing_pool(scsi_debug_devices: list[str]) -> Generator[StratisPool, None, None]:
    """Create test pool with failing devices.

    Creates pool for failure testing:
    - Uses SCSI debug devices
    - Injects device failures
    - Tests error handling
    - Manages cleanup

    Args:
        scsi_debug_devices: SCSI debug device fixture

    Failure Injection:
    - Every operation fails
    - Noisy error reporting
    - Tests error handling
    - Recovery procedures

    Example:
        ```python
        @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
        def test_pool(stratis_failing_pool):
            # Test failure handling
            assert not stratis_failing_pool.stop()
            assert 'error' in stratis_failing_pool.status
        ```
    """
    # Get first device for injection
    device = ScsiDebugDevice(scsi_debug_devices[0])

    # Inject failures (every operation fails with noisy error)
    device.inject_failure(every_nth=1, opts=1)

    # Create pool
    pool = StratisPool()
    pool.name = 'sts-stratis-test-pool'
    pool.blockdevs = [scsi_debug_devices[0]]  # Only use first device

    if not pool.create():
        pytest.skip('Failed to create test pool')

    yield pool

    # Clean up
    pool.destroy()
