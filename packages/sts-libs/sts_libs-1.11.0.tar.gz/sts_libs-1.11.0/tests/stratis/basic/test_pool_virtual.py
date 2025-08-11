# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test Stratis pool management with virtual devices.

This module tests basic Stratis functionality using:
- Loop devices (file-backed block devices)
- SCSI debug devices (kernel module devices)
"""

import logging
import os

import pytest

from sts import lvm

# from sts.stratis.filesystem import StratisFilesystem
from sts.stratis.pool import PoolCreateConfig, StratisPool, TangConfig
from sts.utils.system import SystemManager
from sts.utils.version import VersionInfo


@pytest.mark.usefixtures('_stratis_test')
class TestPoolVirtual:
    """Test Stratis pool management with virtual devices."""

    def setup_method(self) -> None:
        """Set up test method.

        - Ensure stratisd is running
        """
        system = SystemManager()
        if not system.is_service_running('stratisd') and not system.service_start('stratisd'):
            pytest.skip('Could not start stratisd.service')

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_basic_loop(self, loop_devices: list[str]) -> None:
        """Test basic pool operations with loop devices.

        Args:
            loop_devices: Loop device fixture
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Test basic creation
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        assert pool.create()
        assert pool.destroy()

        # Test creation with overprovisioning disabled
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        config = PoolCreateConfig(no_overprovision=True)
        assert pool.create(config)
        assert pool.destroy()

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_encryption(self, loop_devices: list[str], setup_stratis_key: str) -> None:
        """Test pool encryption operations.

        Args:
            loop_devices: Loop device fixture
            setup_stratis_key: Stratis key fixture
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Create encrypted pool
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        config = PoolCreateConfig(key_desc=setup_stratis_key)
        assert pool.create(config)

        # Test stop/start with encryption
        assert pool.stop()
        # stratis changed the unlock method to 'any' in 3.8.0 or using specific token slot
        unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'keyring'
        assert pool.start(unlock_method=unlock_method)
        # Cleanup
        assert pool.destroy()

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_encryption_clevis_thumbprint(
        self, loop_devices: list[str], stratis_clevis_test: dict[str, str]
    ) -> None:
        """Test pool encryption operations.

        Args:
            loop_devices: Loop device fixture
            stratis_clevis_test: Stratis key fixture
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Create encrypted pool
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        config = PoolCreateConfig(
            clevis='tang', tang_url=stratis_clevis_test['url'], thumbprint=stratis_clevis_test['thumbprint']
        )
        assert pool.create(config)
        # Test stop/start with encryption
        assert pool.stop()
        unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'clevis'
        assert pool.start(unlock_method=unlock_method)

        # Cleanup
        assert pool.destroy()

    @pytest.mark.parametrize('loop_devices', [2], indirect=True)
    def test_pool_encryption_clevis_trust(self, loop_devices: list[str], stratis_clevis_test: dict[str, str]) -> None:
        """Test pool encryption operations.

        Args:
            loop_devices: Loop device fixture
            stratis_clevis_test: Stratis key fixture
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Create encrypted pool
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = loop_devices
        config = PoolCreateConfig(clevis='tang', tang_url=stratis_clevis_test['url'], trust_url=True)
        assert pool.create(config)

        # Test stop/start with encryption
        assert pool.stop()
        unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'clevis'
        assert pool.start(unlock_method=unlock_method)
        # Cleanup
        assert pool.destroy()

    @pytest.mark.skip(reason='TODO: Trigger device failure better')
    @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
    def test_pool_failures(self, stratis_failing_pool: StratisPool) -> None:
        """Test pool behavior with failing devices.

        Args:
            stratis_failing_pool: Failing pool fixture
        """
        # The pool is created with a device that fails every other operation
        # Test operations that should fail
        assert not stratis_failing_pool.stop()
        assert not stratis_failing_pool.start()

        # Test operations that should succeed (next operation after failure)
        assert stratis_failing_pool.stop()
        assert stratis_failing_pool.start()

        # Ensure pool is destroyed before scsi_debug devices are removed
        assert stratis_failing_pool.destroy()

    @pytest.mark.skip(reason='TODO: Use multiple devices')
    @pytest.mark.parametrize('scsi_debug_devices', [2], indirect=True)
    def test_pool_cache(self, scsi_debug_devices: list[str]) -> None:
        """Test pool cache operations.

        Args:
            scsi_debug_devices: SCSI debug device fixture (requires  devices)
        """
        pool_name = os.getenv('STRATIS_POOL_NAME', 'sts-stratis-test-pool')

        # Create pool with first device only
        pool = StratisPool()
        pool.name = pool_name
        pool.blockdevs = [scsi_debug_devices[0]]  # Only use first device for data tier
        assert pool.create()
        logging.info(scsi_debug_devices)

        try:
            # Initialize cache with second device
            assert pool.init_cache([scsi_debug_devices[1]])  # Use second device for cache tier

        finally:
            # Ensure pool is destroyed before scsi_debug devices are removed
            assert pool.destroy()


@pytest.mark.usefixtures('_stratis_test')
class TestPoolAddDevices:
    @pytest.mark.parametrize(
        'pool_fixture',
        [
            pytest.param('stratis_key_desc_pool', id='keyring-encryption'),
            pytest.param('stratis_tang_pool', id='tang-encryption'),
            pytest.param('stratis_no_enc_pool', id='no-encryption'),
        ],
    )
    @pytest.mark.parametrize('loop_devices', [4], indirect=True)
    def test_add_data_devices(self, loop_devices: list[str], pool_fixture: str, request: pytest.FixtureRequest) -> None:
        """Test adding data devices to different types of pools.

        Args:
            loop_devices: List of loop devices (4 devices required)
            pool_fixture: Name of the pool fixture to use
            request: Pytest request object to get the fixture
        """
        assert len(loop_devices) == 4, f'Expected 4 loop devices, got {len(loop_devices)}'

        pool = request.getfixturevalue(pool_fixture)

        remaining_devices = loop_devices[2:]  # Use remaining devices
        assert pool.add_data(remaining_devices), 'Failed to add devices to pool'
        logging.info(pool.encryption)
        if pool.encryption:
            assert pool.stop(), 'Failed to stop encrypted pool'
            if 'tang' in pool_fixture:
                unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'clevis'
                assert pool.start(unlock_method=unlock_method)
            elif 'key_desc' in pool_fixture:
                unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'keyring'
                assert pool.start(unlock_method=unlock_method)

    @pytest.mark.parametrize(
        'pool_fixture',
        [
            pytest.param('stratis_key_desc_pool', id='keyring-encryption'),
            pytest.param('stratis_tang_pool', id='tang-encryption'),
            pytest.param('stratis_no_enc_pool', id='no-encryption'),
        ],
    )
    @pytest.mark.parametrize('loop_devices', [5], indirect=True)
    def test_init_cache_add_data(
        self, loop_devices: list[str], pool_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        """Test adding data devices to different types of pools.

        Args:
            loop_devices: List of loop devices (4 devices required)
            pool_fixture: Name of the pool fixture to use
            request: Pytest request object to get the fixture
        """
        assert len(loop_devices) == 5, f'Expected 5 loop devices, got {len(loop_devices)}'

        pool = request.getfixturevalue(pool_fixture)

        assert pool.init_cache([loop_devices[2]])
        assert pool.add_data([loop_devices[3]]), 'Failed to add devices to pool'
        assert pool.add_cache([loop_devices[4]]), 'Failed to add devices to pool'

        if pool.encryption:
            assert pool.stop(), 'Failed to stop encrypted pool'
            if 'tang' in pool_fixture:
                unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'clevis'
                assert pool.start(unlock_method=unlock_method)
            elif 'key_desc' in pool_fixture:
                unlock_method = 'any' if pool.version > VersionInfo(3, 8, 0) else 'keyring'
                assert pool.start(unlock_method=unlock_method)


@pytest.mark.usefixtures('_stratis_test')
class TestPoolBind:
    @pytest.mark.parametrize(
        'pool_fixture',
        [
            pytest.param('stratis_key_desc_pool', id='keyring-encryption'),
            pytest.param('stratis_tang_pool', id='tang-encryption'),
        ],
    )
    @pytest.mark.parametrize('loop_devices', [4], indirect=True)
    def test_bind_rebind(
        self,
        loop_devices: list[str],
        pool_fixture: str,
        request: pytest.FixtureRequest,
        setup_stratis_key: str,
        stratis_clevis_test: dict[str, str],
    ) -> None:
        """Test binding and unbinding for different encryption methods.

        Args:
            pool_fixture: Name of the encrypted pool fixture to use
            request: Pytest request object to get the fixture
            setup_stratis_key: Stratis key fixture for keyring encryption
            stratis_clevis_test: Tang server configuration fixture
        """
        # Get the pre-encrypted pool
        pool = request.getfixturevalue(pool_fixture)

        if 'key_desc' in pool_fixture:
            tang_config = TangConfig(url=stratis_clevis_test['url'], thumbprint=stratis_clevis_test['thumbprint'])
            assert pool.bind_tang(tang_config), 'Failed to bind to Tang'
        else:
            assert pool.bind_keyring(setup_stratis_key), 'Failed to bind to keyring'

        initial_unlock_method = 'keyring' if 'key_desc' in pool_fixture else 'clevis'
        assert pool.stop(), 'Failed to stop initially encrypted pool'
        if pool.version > VersionInfo(3, 8, 0):
            assert pool.start(token_slot=0), 'Failed to start initially encrypted pool'
        else:
            assert pool.start(unlock_method=initial_unlock_method), 'Failed to start initially encrypted pool'
        if 'key_desc' in pool_fixture:
            assert pool.unbind_keyring(), 'Failed to unbind from keyring'
            secondary_unlock_method = 'clevis'
        else:
            assert pool.unbind_clevis(), 'Failed to unbind from Clevis'
            secondary_unlock_method = 'keyring'

        assert pool.add_data([loop_devices[2]])

        assert pool.stop(), 'Failed to stop pool after rebind'
        if pool.version > VersionInfo(3, 8, 0):
            assert pool.start(token_slot=1), 'Failed to start pool after rebind'
        else:
            assert pool.start(unlock_method=secondary_unlock_method), 'Failed to start pool after rebind'


@pytest.mark.usefixtures('_stratis_test')
class TestPoolExtendData:
    @pytest.mark.parametrize(
        'pool_fixture',
        [
            pytest.param('stratis_key_desc_pool', id='keyring-encryption'),
            pytest.param('stratis_tang_pool', id='tang-encryption'),
            pytest.param('stratis_no_enc_pool', id='no-encryption'),
        ],
    )
    @pytest.mark.parametrize('loop_devices', [5], indirect=True)
    def test_extend_data(
        self,
        loop_devices: list[str],
        pool_fixture: str,
        request: pytest.FixtureRequest,
        stratis_extend_lvm: lvm.LogicalVolume,
    ) -> None:
        """Test adding data devices to different types of pools.

        Args:
            loop_devices: List of loop devices (4 devices required)
            pool_fixture: Name of the pool fixture to use
            request: Pytest request object to get the fixture
        """
        assert len(loop_devices) == 5, f'Expected 5 loop devices, got {len(loop_devices)}'

        pool: StratisPool = request.getfixturevalue(pool_fixture)
        lv = stratis_extend_lvm

        assert pool.add_data([str(lv.path)])

        assert pool.report is not None
        assert pool.report.total_size is not None
        total_size_before_extend = pool.report.total_size

        assert lv.extend(extents='100%vg')

        assert pool.extend_data()
        assert pool.report is not None
        assert pool.report.total_size is not None
        assert total_size_before_extend is not None
        assert pool.report.total_size > total_size_before_extend

        logging.info(pool.encryption)
        # Check that we have encryption info if we expect it
        if not pool.encryption and ('key_desc' in pool_fixture or 'tang' in pool_fixture):
            pytest.fail('Pool should be encrypted')

        assert pool.stop(), 'Failed to stop pool'

        if 'tang' in pool_fixture:
            if pool.version > VersionInfo(3, 8, 0):
                assert pool.start(token_slot=0), 'Failed to start pool with Clevis'
            else:
                assert pool.start(unlock_method='clevis'), 'Failed to start pool with Clevis'
            return
        if 'key_desc' in pool_fixture:
            if pool.version > VersionInfo(3, 8, 0):
                assert pool.start(token_slot=0), 'Failed to start pool with keyring'
            else:
                assert pool.start(unlock_method='keyring'), 'Failed to start pool with keyring'
            return
        # No encryption, so we should be able to start with any method
        assert pool.start()
