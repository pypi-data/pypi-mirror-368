# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""RDMA bug reproducers."""

import pytest

from sts.utils.cmdline import run


@pytest.mark.usefixtures('_exists_rdma')
class TestReproducers:
    """A set of bug reproducers."""

    @staticmethod
    def test_23034_warnings_speed_unknown() -> None:
        """Verify no unexpected warning message is shown.

        When a multiple port adapter has one port connected and one not connected,
        running ibv_devinfo will trigger a similar message:<port> speed is unknown, defaulting to 1000.
        """
        warning_msg = '"speed is unknown, defaulting to 1000"'
        assert run(f'dmesg -c | grep {warning_msg}').exit_status == 1
        run('ibv_devinfo')
        assert run(f'dmesg -c | grep {warning_msg}').exit_status == 1
