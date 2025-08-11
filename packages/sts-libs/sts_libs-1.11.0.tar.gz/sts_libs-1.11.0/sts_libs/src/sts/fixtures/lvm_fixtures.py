# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""LVM test fixtures.

This module provides fixtures for testing LVM (Logical Volume Management):
- Package installation and cleanup
- Service management
- Device configuration
- VDO (Virtual Data Optimizer) support

Fixture Dependencies:
1. _lvm_test (base fixture)
   - Installs LVM packages
   - Manages volume cleanup
   - Logs system information

2. _vdo_test (depends on _lvm_test)
   - Installs VDO packages
   - Manages kernel module
   - Provides data reduction features

Common Usage:
1. Basic LVM testing:
   @pytest.mark.usefixtures('_lvm_test')
   def test_lvm():
       # LVM utilities are installed
       # Volumes are cleaned up after test

2. VDO-enabled testing:
   @pytest.mark.usefixtures('_vdo_test')
   def test_vdo():
       # VDO module is loaded
       # Data reduction is available

Error Handling:
- Package installation failures fail the test
- Module loading failures fail the test
- Volume cleanup runs even if test fails
- Service issues are logged
"""

from __future__ import annotations

import logging
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.files import Directory, mkfs, mount, umount
from sts.utils.modules import ModuleManager
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from collections.abc import Generator

    from sts.blockdevice import BlockDevice

# Constants
LVM_PACKAGE_NAME = 'lvm2'
VDO_PACKAGE_NAME = 'vdo'


@pytest.fixture(scope='class')
def _lvm_test() -> Generator:
    """Set up LVM environment.

    This fixture provides the foundation for LVM testing:
    - Installs LVM utilities (lvm2 package)
    - Logs system information for debugging
    - Cleans up volumes before and after test
    - Ensures consistent test environment

    Package Installation:
    - lvm2: Core LVM utilities
    - Required device-mapper modules

    Volume Cleanup:
    1. Deactivates all volume groups
    2. Removes all physical volumes
    3. Runs before and after each test class
    4. Handles force removal if needed

    System Information:
    - Kernel version
    - LVM version
    - Device-mapper status

    Example:
        ```python
        @pytest.mark.usefixtures('_lvm_test')
        def test_lvm():
            # Create and test LVM volumes
            # Volumes are automatically cleaned up
        ```
    """
    system = SystemManager()
    assert system.package_manager.install(LVM_PACKAGE_NAME)
    logging.info(f'Kernel version: {system.info.kernel}')

    # Clean up existing volumes
    run('vgchange -an')  # Deactivate all VGs
    run('pvremove -ff -y $(pvs -o pv_name --noheadings 2>/dev/null)')  # Remove all PVs

    yield

    # Clean up volumes
    run('vgchange -an')  # Deactivate all VGs
    run('pvremove -ff -y $(pvs -o pv_name --noheadings 2>/dev/null)')  # Remove all PVs


@pytest.fixture(scope='class')
def _vdo_test(_lvm_test: None) -> Generator:
    """Set up VDO environment.

    Args:
       _lvm_test: LVM test fixture required for VDO functionality

    Features:
       - Deduplication, compression, thin provisioning
       - Automatic module loading/unloading
       - Cleanup of VDO resources

    Example:
       @pytest.mark.usefixtures('_vdo_test')
       def test_vdo():
           # Test VDO functionality
           pass
    """
    module = 'dm-vdo'
    system = SystemManager()
    assert system.package_manager.install(VDO_PACKAGE_NAME)
    try:
        k_version = system.info.kernel
        if k_version:
            k_version = k_version.split('.')
            # dm-vdo is available from kernel 6.9, for older version it's available
            # from kmod-kvdo package
            if int(k_version[0]) < 6 or (int(k_version[0]) == 6 and int(k_version[1]) <= 8):
                logging.info('Using kmod-kvdo')
                assert system.package_manager.install('kmod-kvdo')
                module = 'kvdo'
    except (ValueError, IndexError):
        # if we can't get kernel version, just try to load dm-vdo
        logging.warning('Unable to parse kernel version; defaulting to dm-vdo')

    kmod = ModuleManager()
    assert kmod.load(name=module)

    yield

    # Unload module
    kmod.unload(name=module)


@pytest.fixture
def setup_vg(ensure_minimum_devices_with_same_block_sizes: list[BlockDevice]) -> Generator[str, None, None]:
    """Set up an LVM Volume Group (VG) with Physical Volumes (PVs) for testing.

    This fixture creates a Volume Group using the provided block devices. It handles the creation
    of Physical Volumes from the block devices and ensures proper cleanup after tests, even if
    they fail.

    Args:
        ensure_minimum_devices_with_same_block_sizes: List of BlockDevice objects with matching
            block sizes to be used for creating Physical Volumes.

    Yields:
        str: Name of the created Volume Group.

    Raises:
        AssertionError: If PV creation fails for any device.

    Example:
        def test_volume_group(setup_vg):
            vg_name = setup_vg
            # Use vg_name in your test...
    """
    vg_name = getenv('STS_VG_NAME', 'stsvg0')
    pvs = []

    try:
        # Create PVs
        for device in ensure_minimum_devices_with_same_block_sizes:
            device_name = str(device.path).replace('/dev/', '')
            device_path = str(device.path)

            pv = lvm.PhysicalVolume(name=device_name, path=device_path)
            assert pv.create(), f'Failed to create PV on device {device_path}'
            pvs.append(pv)

        # Create VG
        vg = lvm.VolumeGroup(name=vg_name, pvs=[pv.path for pv in pvs])
        assert vg.create(), f'Failed to create VG {vg_name}'

        yield vg_name

    finally:
        # Cleanup in reverse order
        vg = lvm.VolumeGroup(name=vg_name)
        if not vg.remove():
            logging.warning(f'Failed to remove VG {vg_name}')

        for pv in pvs:
            if not pv.remove():
                logging.warning(f'Failed to remove PV {pv.path}')


@pytest.fixture
def lv_quarter_of_vg(_lvm_test: None, setup_vg: str) -> Generator[str, None, None]:
    """Create a logical volume using 25% of a volume group.

    Creates:
    - Logical volume 'lv1' using 25% of VG space

    Yields:
        str: device path
    """
    lv_name = getenv('LV_NAME', 'stscow25vglv1')
    vg_name = setup_vg
    # Create LV
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.create(extents='25%vg')

    yield f'/dev/{vg_name}/{lv_name}'

    # Cleanup
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.remove()


@pytest.fixture
def thin_lv_quarter_of_vg(_lvm_test: None, setup_vg: str) -> Generator[str, None, None]:
    """Create a thin logical volume using a thin pool that uses 25% of a volume group.

    Creates:
    - Thin pool using 25% of the provided volume group space
    - Thin logical volume with 512MB virtual size

    Yields:
        str: Device path to the thin logical volume

    """
    lv_name = getenv('LV_NAME', 'ststhin25vglv1')
    vg_name = setup_vg
    pool_name = getenv('THIN_POOL_NAME', 'stspool1_25vg')

    # Create thin pool
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.create(
        type='thin',
        thinpool=pool_name,
        extents='25%VG',
        virtualsize='512M',
    )

    yield f'/dev/{vg_name}/{lv_name}'

    # Cleanup
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.remove()

    pool_lv = lvm.LogicalVolume(name=pool_name, vg=vg_name)
    assert pool_lv.remove()


@pytest.fixture
def mount_lv(lv_quarter_of_vg: str) -> Generator[Directory, None, None]:
    """Mount a logical volume on a test directory.

    Args:
        lv_quarter_of_vg: Fixture providing LV info

    Yields:
        Directory: Directory representation of mount point
    """
    dev_path = lv_quarter_of_vg
    mount_point = getenv('STS_LV_MOUNT_POINT', '/mnt/lvcowmntdir')

    # Create filesystem on the LV
    assert mkfs(device=dev_path, fs_type='xfs')

    # Create mount point directory using Directory class
    mnt_dir = Directory(Path(mount_point), create=True)
    assert mnt_dir.exists, f'Failed to create mount point directory {mount_point}'

    # Mount the LV
    assert mount(device=dev_path, mountpoint=mount_point)

    yield mnt_dir

    # Cleanup
    assert umount(mountpoint=mount_point)
    mnt_dir.remove_dir()


@pytest.fixture
def mount_thin_lv(thin_lv_quarter_of_vg: str) -> Generator[Directory, None, None]:
    """Mount a thin logical volume on a test directory.

    Args:
        thin_lv_quarter_of_vg: Fixture providing thin LV info

    Yields:
        Directory: Directory representation of mount point
    """
    dev_path = thin_lv_quarter_of_vg
    mount_point = getenv('STS_THIN_LV_MOUNT_POINT', '/mnt/thinlvmntdir')

    # Create filesystem on the thin LV
    assert mkfs(device=dev_path, fs_type='xfs')

    # Create mount point directory using Directory class
    mnt_dir = Directory(Path(mount_point), create=True)
    assert mnt_dir.exists, f'Failed to create mount point directory {mount_point}'

    # Mount the LV
    assert mount(device=dev_path, mountpoint=mount_point)

    yield mnt_dir

    # Cleanup
    assert umount(mountpoint=mount_point)
    mnt_dir.remove_dir()


def _create_multiple_lv_mntpoints(
    vg_name: str,
    lv_type: str = 'cow',
    lv_name: str | None = None,
    mount_point: str | None = None,
    pool_name: str | None = None,
    fs_type: str | None = None,
    num_of_mntpoints: int | None = None,
    virtualsize: str | None = None,
    percentage_of_vg_to_use: int | None = None,
) -> Generator[list[Directory], None, None]:
    """Creating multiple logical volumes with mounted filesystems.

    Args:
        vg_name: Volume group name
        lv_type: Type of logical volume ('cow' or 'thin')
        lv_name: Base name for logical volumes (defaults based on lv_type)
        mount_point: Base mount point path (defaults based on lv_type)
        pool_name: Base name for thin pools (only used for thin LVs)
        fs_type: Filesystem type (defaults to env var or 'xfs')
        num_of_mntpoints: Number of mount points (defaults to env var or 6)
        virtualsize: Virtual size for thin logical volumes (defaults to '512M')
        percentage_of_vg_to_use: Percentage of volume group to use across all LVs (defaults to 50)

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    # Set defaults based on lv_type
    if lv_type == 'thin':
        default_lv_name = 'ststhinmultiplemntpoints'
        default_mount_point = '/mnt/lvthinmntdir'
        default_pool_name = 'stspool1mutiplethin'
    else:  # cow
        default_lv_name = 'stscowmultiplemntpoints'
        default_mount_point = '/mnt/lvcowmntdir'
        default_pool_name = None
    percentage_of_vg_to_use = percentage_of_vg_to_use or 50
    default_virtualsize = '512M'
    # Use provided values or fall back to environment variables or defaults
    lv_name = lv_name or getenv('LV_NAME', default_lv_name)
    mount_point = mount_point or getenv('STS_LV_MOUNT_POINT', default_mount_point)
    fs_type = fs_type or getenv('STS_LV_FS_TYPE', 'xfs')
    virtualsize = virtualsize or getenv('STS_LV_VIRTUALSIZE', default_virtualsize)

    if lv_type == 'thin':
        pool_name = pool_name or getenv('STS_THIN_POOL_NAME', default_pool_name)

    if num_of_mntpoints is None:
        try:
            num_of_mntpoints = int(getenv('STS_COW_MNTPOINT_NUMBER', '6'))
        except (ValueError, TypeError):
            pytest.fail('STS_COW_MNTPOINT_NUMBER variable has incorrect value!')

    vg_percentage = int(percentage_of_vg_to_use / int(num_of_mntpoints))
    sources: list[Directory] = []
    logical_volumes: list[lvm.LogicalVolume] = []

    # Create LV
    for num in range(num_of_mntpoints):
        lv = lvm.LogicalVolume(name=f'{lv_name}{num}', vg=vg_name)
        logical_volumes.append(lv)

        # Create LV based on type
        if lv_type == 'thin':
            assert lv.create(
                type='thin',
                thinpool=f'{pool_name}{num}',
                extents=f'{vg_percentage}%vg',
                virtualsize=virtualsize,
            )
        elif lv_type == 'cow':
            assert lv.create(extents=f'{vg_percentage}%vg')
        else:
            pytest.fail(f'Invalid LV type: {lv_type}')

        dev_path = f'/dev/{vg_name}/{lv_name}{num}'
        assert mkfs(device=dev_path, fs_type=fs_type)

        mnt_dir = Directory(Path(f'{mount_point}{num}'), create=True)
        assert mnt_dir.exists, f'Failed to create mount point directory {mount_point}{num}'
        # Mount the LV
        assert mount(device=dev_path, mountpoint=f'{mount_point}{num}')
        sources.append(mnt_dir)

    yield sources

    # Cleanup
    for num in range(num_of_mntpoints):
        assert umount(mountpoint=f'{mount_point}{num}')
        mnt_dir = Directory(Path(f'{mount_point}{num}'), create=True)
        mnt_dir.remove_dir()
    for lv in logical_volumes:
        assert lv.remove()


@pytest.fixture
def prepare_multiple_cow_mntpoints(
    _lvm_test: None, setup_vg: str, request: pytest.FixtureRequest
) -> Generator[list[Directory], None, None]:
    """Create multiple COW logical volumes with mounted filesystems for testing.

    This fixture creates multiple logical volumes within a volume group, formats them
    with filesystems, and mounts them to separate mount points. It's designed for
    testing Copy-on-Write (COW) snapshots with multiple source volumes.

    Supports parameter customization via pytest.param or environment variables.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    # Get parameters from request if provided, otherwise use environment variables
    params = getattr(request, 'param', {})

    yield from _create_multiple_lv_mntpoints(
        vg_name=setup_vg,
        lv_type='cow',
        **params,
    )


@pytest.fixture
def prepare_multiple_thin_mntpoints(
    _lvm_test: None, setup_vg: str, request: pytest.FixtureRequest
) -> Generator[list[Directory], None, None]:
    """Create multiple thin logical volumes with mounted filesystems for testing.

    This fixture creates multiple thin logical volumes within a volume group, each with
    its own thin pool, formats them with filesystems, and mounts them to separate mount
    points. It's designed for testing thin provisioning scenarios with multiple volumes.

    Supports parameter customization via pytest.param or environment variables.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    # Get parameters from request if provided, otherwise use environment variables
    params = getattr(request, 'param', {})

    yield from _create_multiple_lv_mntpoints(
        vg_name=setup_vg,
        lv_type='thin',
        **params,
    )


@pytest.fixture
def prepare_multiple_cow_mntpoints_ext4(_lvm_test: None, setup_vg: str) -> Generator[list[Directory], None, None]:
    """Create multiple COW logical volumes with ext4 filesystems for testing.

    This is a convenience wrapper that configures COW logical volumes
    to use ext4 filesystem by default.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    yield from _create_multiple_lv_mntpoints(vg_name=setup_vg, lv_type='cow', fs_type='ext4')


@pytest.fixture
def prepare_multiple_thin_mntpoints_ext4(_lvm_test: None, setup_vg: str) -> Generator[list[Directory], None, None]:
    """Create multiple thin logical volumes with ext4 filesystems for testing.

    This is a convenience wrapper that configures thin logical volumes
    to use ext4 filesystem by default.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    yield from _create_multiple_lv_mntpoints(vg_name=setup_vg, lv_type='thin', fs_type='ext4')
