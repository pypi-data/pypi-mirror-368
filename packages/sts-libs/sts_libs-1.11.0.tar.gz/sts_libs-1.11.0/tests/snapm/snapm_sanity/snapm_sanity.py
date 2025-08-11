# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv
from typing import TYPE_CHECKING

import pytest

from sts.lvm import LogicalVolume
from sts.snapm.snapset import Snapset
from sts.utils.files import count_files
from sts.utils.version import VersionInfo

if TYPE_CHECKING:
    from sts.utils.files import Directory


@pytest.mark.usefixtures('_snapm_test')
class TestSnapm:
    @pytest.mark.parametrize(
        'fixture_name',
        [
            pytest.param('mount_lv', id='lvm2-cow'),
            pytest.param('mount_thin_lv', id='lvm2-thin'),
        ],
    )
    def test_lvm2_snapshots(self, request: pytest.FixtureRequest, fixture_name: str) -> None:
        """Test basic snapset operations with LVM.

        Tests the creation, listing, renaming, and deletion of snapsets
        on mounted LVM volumes.

        Args:
            request: pytest request fixture
            fixture_name: name of the fixture providing a mounted LV
        """
        snapset_name = getenv('STS_SNAPSET_NAME', 'stssnapset1')
        snapset_rename = getenv('STS_SNAPSET_RENAME', 'stssnapsetrename')
        mount_point: Directory = request.getfixturevalue(fixture_name)
        n_files = count_files(mount_point.path)
        flag = mount_point.path / 'FLAG'
        flag.write_text('SNAPMTEST')

        assert flag.exists

        # Create snapset using the new Snapset class
        snapset = Snapset()
        assert snapset.create(snapset_name=snapset_name, size_policy='80%FREE', sources=[str(mount_point.path)]), (
            f'Failed to create snapset {snapset_name}'
        )

        # Verify that LVM snapshot was created
        lv = LogicalVolume()
        lv_result = lv.lvs()
        assert lv_result.succeeded
        assert f'snapset_{snapset_name}' in lv_result.stdout

        assert snapset.rename(snapset_rename), f'Failed to rename snapset from {snapset_name} to {snapset_rename}'
        if snapset.info:
            assert snapset.info.name == snapset_rename

        assert count_files(mount_point.path) == n_files + 1
        mount_point.remove_file(flag)
        assert count_files(mount_point.path) == n_files

        # Activate/Deactivate doesn't have effect on COW snapshots
        if 'thin' in fixture_name and snapset.info:
            assert snapset.activate()
            assert snapset.info.status == 'Active'

            assert snapset.deactivate()
            assert snapset.info.status == 'Inactive'

            assert snapset.autoactivate(enable=True)
            assert snapset.info.autoactivate is True

            assert snapset.autoactivate(enable=False)
            assert snapset.info.autoactivate is False

        assert snapset.delete(), f'Failed to delete snapset {snapset_rename}'

        lv_result = lv.lvs()
        assert f'snapset_{snapset_rename}' not in lv_result.stdout

    @pytest.mark.parametrize(
        'fixture_name',
        [
            pytest.param('prepare_multiple_cow_mntpoints', id='lvm2-cow-xfs'),
            pytest.param('prepare_multiple_thin_mntpoints', id='lvm2-thin-xfs'),
            pytest.param('prepare_multiple_cow_mntpoints_ext4', id='lvm2-cow-ext4'),
            pytest.param('prepare_multiple_thin_mntpoints_ext4', id='lvm2-thin-ext4'),
        ],
    )
    def test_lvm2_snapshots_split_prune(self, request: pytest.FixtureRequest, fixture_name: str) -> None:
        snapset = Snapset()
        if snapset.version < VersionInfo.from_string('0.4.3'):
            pytest.skip('requires snapm-0.4.3 or higher')
        sources = request.getfixturevalue(fixture_name)
        mntpoints = [str(source.path) for source in sources]
        snapset_name = getenv('STS_SNAPSET_NAME', 'stssnapset1')
        snapset_rename = getenv('STS_SNAPSET_RENAME', 'stssnapsetrename')
        snapset_single = getenv('STS_SNAPM_SPLIT_SINGLE', 'stssnapsetsplitsingle')
        assert snapset.create(snapset_name=snapset_name, sources=mntpoints), f'Failed to create snapset {snapset_name}'
        # split multiple
        assert snapset.info
        assert snapset.info.mount_points
        assert len(snapset.info.mount_points) == len(sources)
        splitsnapset = snapset.split(new_name=snapset_rename, sources=mntpoints[:4])
        assert splitsnapset.info is not None
        assert splitsnapset.info.name is not None
        assert splitsnapset.info.name == snapset_rename
        assert splitsnapset.info.mount_points is not None
        # split single
        splitsingle = snapset.split(new_name=snapset_single, sources=[mntpoints[-1]])
        assert splitsingle.info is not None
        assert splitsingle.info.name is not None
        assert splitsingle.info.name == snapset_single
        assert splitsingle.info.mount_points is not None
        # prune multiple
        assert mntpoints[0] not in snapset.info.mount_points
        # attempt to prune everything, this should fail
        assert not splitsnapset.prune(mntpoints[:4])
        # make sure all mountpoints are still there
        assert len(splitsnapset.info.mount_points) == len(mntpoints[:4])
        assert splitsnapset.prune(mntpoints[:4][:2])
        assert mntpoints[0] not in splitsnapset.info.mount_points
        # prune single
        assert splitsnapset.prune([mntpoints[3]])
        assert mntpoints[3] not in splitsnapset.info.mount_points
        snapset.delete()
        splitsnapset.delete()
        splitsingle.delete()
