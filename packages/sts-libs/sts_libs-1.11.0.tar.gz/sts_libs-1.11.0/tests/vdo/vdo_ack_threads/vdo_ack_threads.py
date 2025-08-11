# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv

from sts.lvm import LogicalVolume, PhysicalVolume, VolumeGroup
from sts.utils.cmdline import run


def test_ack_threads() -> None:
    vg_name = getenv('VDO_VG_NAME', 'vdovg')
    lv_name = getenv('VDO_LV_NAME', 'vdolv')
    ack_threads = getenv('VDO_ACK_THREADS', '0 1 100')
    values = ack_threads.split()

    # Create PV and VG
    pv = PhysicalVolume(path='/dev/sda')
    assert pv.create()
    vg = VolumeGroup(name=vg_name, pvs=['/dev/sda'])
    assert vg.create()

    # Test different ack_threads values
    for value in values:
        # Create VDO LV
        lv = LogicalVolume(name=lv_name, vg=vg_name)
        assert lv.create(extents='5%vg', vdosettings=f'vdo_ack_threads={value}')

        # Verify ack_threads setting
        assert f'ack {value}' in run(f'dmsetup table {vg_name}-vpool0-vpool').stdout

        # Clean up LV
        assert lv.remove()

    # Clean up VG and PV
    assert vg.remove()
    assert pv.remove()
