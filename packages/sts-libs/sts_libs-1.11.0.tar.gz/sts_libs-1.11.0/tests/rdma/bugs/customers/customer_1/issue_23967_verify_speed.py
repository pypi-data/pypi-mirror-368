# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv

from sts import rdma


def test_speed() -> None:
    hca_id = getenv('RDMA_HCA_ID', 'mlx5_0')
    port_id = getenv('RDMA_PORT', '1')
    actual_speed = getenv('RDMA_ACTUAL_SPEED', '100')

    device = rdma.RdmaDevice(hca_id)
    port = device.get_port(port_id)
    netdev = device.get_netdev(port_id)

    assert port is not None
    assert netdev is not None
    assert port.rate_speed == actual_speed
    # speed is dynamically added from sysfs
    assert int(actual_speed) == int(netdev.speed) / 1000  # type: ignore[attr-defined]
