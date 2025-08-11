# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

from os import getenv

import pytest

hca_id = getenv('RDMA_HCA_ID', 'mlx5_0')
vf_num = getenv('VF_NUMBER', '2')


@pytest.fixture(scope='class')
def _rdma_sriov_test(request, rdma_device) -> None:  # noqa: ANN001
    """Create Sriov instance for the class where users use this fixture. When parameter scope = "class",
     multiple test cases in class will get executed and will only call this function once.

    Args:
        request: Store sriov in request variable at a class level which can be accessed while running test,
        referring to https://docs.pytest.org/en/stable/reference/reference.html#request.

        rdma_device: Fixture rdma_device

    Returns: None
    """
    request.cls.device = rdma_device(hca_id)
    if not request.cls.device.is_sriov_capable:
        pytest.skip(reason='No sriov support')
    request.cls.sriov = request.cls.device.get_sriov()


@pytest.mark.usefixtures('_exists_rdma', '_rdma_sriov_test')
class TestRdmaSriov:
    """RDMA sriov test suite."""

    def test_enable_vf(self) -> None:
        self.sriov.set_sriov_numvfs(vf_num)  # type: ignore[attr-defined]
        assert self.sriov.sriov_numvfs == vf_num  # type: ignore[attr-defined]

    def test_disable_vf(self) -> None:
        self.sriov.set_sriov_numvfs('0')  # type: ignore[attr-defined]
        assert self.sriov.sriov_numvfs == '0'  # type: ignore[attr-defined]
