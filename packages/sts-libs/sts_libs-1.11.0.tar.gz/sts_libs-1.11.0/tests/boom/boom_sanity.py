# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv

import pytest

from sts.boom.entry import BoomEntry
from sts.boom.host import BoomHost
from sts.boom.profile import BoomProfile
from sts.utils.system import SystemInfo, SystemManager


@pytest.mark.usefixtures('_boom_test')
class TestBoom:
    # Get system information
    system_info = SystemInfo.get_current()
    system_manager = SystemManager()
    if system_info.distribution:
        uname_pattern = (
            f'fc{system_info.version.major}'
            if system_info.distribution.lower() == 'fedora'
            else f'el{system_info.version.major}'
        )
    else:
        uname_pattern = f'el{system_info.version.major}'
    os_name = getenv('STS_BOOM_OS_NAME', 'Red Hat Enterprise Linux')
    os_version = getenv('STS_BOOM_OS_VERSION', '6.0')
    os_short_name = getenv('STS_BOOM_SHORT_NAME', 'RHEL')

    @pytest.mark.usefixtures('profile_from_host')
    def test_profile_creation_from_host(self, profile_from_host: BoomProfile) -> None:
        """Test OS profile creation and deletion.

        Creates a profile for the current host and verifies it can
        be properly deleted.
        """
        profile = profile_from_host

        assert profile.short_name == self.system_info.distribution
        assert profile.version_id == self.system_info.release

    @pytest.mark.usefixtures('profile_from_host')
    def test_profile_clone(self, profile_from_host: BoomProfile) -> None:
        """Test OS profile cloning functionality.

        Creates a profile, clones it with modified attributes,
        and verifies both the original and cloned profiles.
        """
        profile = profile_from_host

        # Clone the profile with modifications
        # Create a hypothetical next version
        next_version = str(int(self.system_info.version.major) + 1)
        cloned_profile = profile.clone(version=next_version, version_id=next_version, uname_pattern=f'el{next_version}')
        assert cloned_profile is not None
        assert cloned_profile.os_id is not None
        assert cloned_profile.os_id != profile.os_id

        # Verify original profile attributes
        profile.refresh_info()
        assert profile.name == 'Red Hat Enterprise Linux'
        if profile.version:
            assert str(self.system_info.version.major) in profile.version

        # Verify cloned profile attributes
        assert cloned_profile.name == 'Red Hat Enterprise Linux'
        assert cloned_profile.version == next_version
        assert cloned_profile.uname_pattern == f'el{next_version}'

        assert cloned_profile.delete()

    @pytest.mark.usefixtures('default_host_profile')
    def test_host_clone(self, default_host_profile: BoomHost) -> None:
        """Test host profile management operations.

        Creates an OS profile and host profile, then tests editing,
        listing.
        """
        host = default_host_profile
        cloned_host = host.clone(label='test')
        assert cloned_host is not None
        assert cloned_host.host_label == 'test'
        assert cloned_host.host_id != host.host_id
        assert cloned_host.delete()

    @pytest.mark.usefixtures('default_boom_entry')
    def test_entry_cloning(self, default_boom_entry: BoomEntry) -> None:
        """Test boot entry cloning.

        Creates a profile and boot entry, clones it with modifications,
        and verifies the results.
        """
        entry = default_boom_entry
        assert entry.boot_id is not None

        cloned_entry = entry.clone(
            title=f'BOOM-RHEL-{self.system_info.version.major}-CLONE',
        )
        assert cloned_entry is not None
        assert cloned_entry.boot_id is not None
        assert cloned_entry.boot_id != entry.boot_id

        assert cloned_entry.delete()
