# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv

import pytest

from sts.fio.fio import FIO
from sts.utils.cmdline import run


def run_fio_stress(device: str) -> None:
    f = FIO(filename=device)
    f.load_fs_params()
    f.update_parameters({'runtime': '120'})  # adding runtime cap of 2 minutes
    f.run()


@pytest.mark.usefixtures('vdo_test')
def test_xfs_stress(vdo_test: dict) -> None:
    mount_point = getenv('VDO_MOUNT_POINT', '/mnt/vdo_xfs_test')
    vdo_dict = vdo_test

    # Create XFS filesystem
    assert run(f'mkfs.xfs -fK {vdo_dict["dev_path"]}').succeeded

    # Create mount point and mount device
    assert run(f'mkdir -p {mount_point}').succeeded
    assert run(f'mount {vdo_dict["dev_path"]} {mount_point}').succeeded

    # Run FIO stress test
    run_fio_stress(f'{mount_point}/file')

    # Cleanup
    assert run(f'umount {mount_point}').succeeded
    assert run(f'rmdir {mount_point}').succeeded
