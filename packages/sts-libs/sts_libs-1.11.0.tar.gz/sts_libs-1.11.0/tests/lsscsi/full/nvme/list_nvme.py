# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test suite for NVMe device detection in lsscsi.

This module validates lsscsi's NVMe device detection functionality:
- Verifies NVMe device presence using multiple detection methods
- Tests lsscsi output format for NVMe devices
- Handles distribution-specific NVMe detection behavior
"""

from __future__ import annotations

import re

import pytest

from sts.utils.cmdline import run
from sts.utils.system import SystemInfo

# Constants
UTILITY = 'lsscsi'
NVME_DEVICE_PATTERN = re.compile(
    r'/dev/nvme\d+'
)  # Don't anchor with ^ and $ since device path can appear anywhere in line


def get_nvme_count() -> int:
    """Get the number of NVMe devices on the system.

    Returns:
        int: Number of NVMe devices found
    """
    result = run('lsblk -d -n -o NAME')
    return sum(1 for line in result.stdout.splitlines() if line.strip().startswith('nvme'))


@pytest.mark.usefixtures('ensure_nvme_disks')
class TestLsscsiNvme:
    """Test suite for lsscsi NVMe device detection."""

    def test_list_nvme(self) -> None:
        """Test lsscsi NVMe device detection based on distribution version.

        RHEL 9: Should show NVMe devices
        RHEL 10: Should not show NVMe devices (by design)
        """
        info = SystemInfo()
        result = run(UTILITY)
        nvme_count = get_nvme_count()

        # Use search() since device path can appear anywhere in the line
        nvme_found = any(NVME_DEVICE_PATTERN.search(line) for line in result.stdout.splitlines())

        if info.distribution == 'rhel':
            if info.version.major == '9':
                assert nvme_found, (
                    f'NVMe device not found in lsscsi output on RHEL 9 ({nvme_count} NVMe devices detected on system)'
                )
            elif info.version.major == '10':
                assert not nvme_found, (
                    'NVMe devices unexpectedly found in lsscsi output on RHEL 10 '
                    '(by design, NVMe devices should not be shown)'
                )

    def test_nvme_device_format(self) -> None:
        """Verify NVMe device formatting in lsscsi output."""
        if SystemInfo().distribution == 'rhel' and SystemInfo().version.major == '10':
            pytest.skip('RHEL 10 does not show NVMe devices in lsscsi')

        result = run(f'{UTILITY} -l')
        assert result.succeeded, f'Command failed: {UTILITY} -l'

        for line in result.stdout.splitlines():
            if NVME_DEVICE_PATTERN.search(line):  # Use search() since device path can appear anywhere in line
                assert 'nvme' in line.lower(), f"NVMe device path found but 'nvme' not in device info: {line}"

    def test_nvme_exclusion(self) -> None:
        """Test explicit NVMe device exclusion with -N option."""
        result = run(f'{UTILITY} -N')
        assert result.succeeded, f'Command failed: {UTILITY} -N'

        assert not any(
            NVME_DEVICE_PATTERN.search(line)  # Use search() since device path can appear anywhere in line
            for line in result.stdout.splitlines()
        ), 'NVMe devices found in output despite -N option'
