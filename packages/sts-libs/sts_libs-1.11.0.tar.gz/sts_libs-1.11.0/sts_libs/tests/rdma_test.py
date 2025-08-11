# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test RDMA functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from sts.rdma import NetDev, Port, Power, RdmaDevice, Sriov, exists_device, exists_rdma


def test_exists_rdma() -> None:
    """Test RDMA device existence check."""
    with patch('pathlib.Path.is_dir') as mock_is_dir:
        mock_is_dir.return_value = True
        assert exists_rdma() is True

        mock_is_dir.return_value = False
        assert exists_rdma() is False


def test_exists_device() -> None:
    """Test specific RDMA device existence check."""
    with patch('pathlib.Path.is_dir') as mock_is_dir:
        mock_is_dir.return_value = True
        assert exists_device('mlx5_0') is True

        mock_is_dir.return_value = False
        assert exists_device('invalid') is False


def create_mock_file(name: str, content: str) -> MagicMock:
    """Create a mock file with name and content."""
    mock_file = MagicMock()
    mock_file.name = name
    mock_file.stem = name
    mock_file.read_text.return_value = content
    return mock_file


class TestPort:
    """Test Port class."""

    def test_init(self) -> None:
        """Test port initialization."""
        path = Path('/sys/class/infiniband/mlx5_0/ports/1')
        with patch('pathlib.Path.iterdir') as mock_iterdir, patch('pathlib.Path.is_file') as mock_is_file:
            # Create mock files
            mock_files = {
                'rate': create_mock_file('rate', '100 Gb/sec (4X EDR)'),
                'state': create_mock_file('state', '4: ACTIVE'),
                'phys_state': create_mock_file('phys_state', '5: LinkUp'),
            }
            mock_iterdir.return_value = mock_files.values()
            mock_is_file.return_value = True

            port = Port(path)
            assert port.name == '1'
            assert port.rate == '100 Gb/sec (4X EDR)'
            assert port.state == '4: ACTIVE'
            assert port.phys_state == '5: LinkUp'
            assert port.rate_speed == '100'
            assert port.rate_unit == 'Gb/sec'
            assert port.rate_info == '4X EDR'
            assert port.state_num == '4'
            assert port.state_str == 'ACTIVE'
            assert port.phys_state_num == '5'
            assert port.phys_state_str == 'LinkUp'


class TestPower:
    """Test Power class."""

    def test_init(self) -> None:
        """Test power initialization."""
        path = Path('/sys/class/infiniband/mlx5_0')
        with (
            patch('pathlib.Path.is_dir') as mock_is_dir,
            patch('pathlib.Path.iterdir') as mock_iterdir,
            patch('pathlib.Path.is_file') as mock_is_file,
        ):
            mock_is_dir.return_value = True
            mock_file = create_mock_file('control', 'auto')
            mock_iterdir.return_value = [mock_file]
            mock_is_file.return_value = True

            power = Power(path)
            assert power.control == 'auto'


class TestNetDev:
    """Test NetDev class."""

    def test_init(self) -> None:
        """Test network device initialization."""
        path = Path('/sys/class/net/eth0')
        with patch('pathlib.Path.iterdir') as mock_iterdir, patch('pathlib.Path.is_file') as mock_is_file:
            mock_file = create_mock_file('dev_port', '0')
            mock_iterdir.return_value = [mock_file]
            mock_is_file.return_value = True

            netdev = NetDev(path)
            assert netdev.dev_port == '0'


class TestSriov:
    """Test Sriov class."""

    def test_init(self) -> None:
        """Test SR-IOV initialization."""
        path = Path('/sys/class/infiniband/mlx5_0/device')
        with (
            patch('pathlib.Path.is_dir') as mock_is_dir,
            patch('pathlib.Path.iterdir') as mock_iterdir,
            patch('pathlib.Path.is_file') as mock_is_file,
        ):
            mock_is_dir.return_value = True
            mock_files = {
                'sriov_numvfs': create_mock_file('sriov_numvfs', '0'),
                'sriov_totalvfs': create_mock_file('sriov_totalvfs', '8'),
            }
            mock_iterdir.return_value = mock_files.values()
            mock_is_file.return_value = True

            sriov = Sriov(path)
            assert sriov.sriov_numvfs == '0'
            assert sriov.sriov_totalvfs == '8'

    def test_set_numvfs(self) -> None:
        """Test setting number of VFs."""
        path = Path('/sys/class/infiniband/mlx5_0/device')
        with (
            patch('pathlib.Path.is_file') as mock_is_file,
            patch('pathlib.Path.write_text') as mock_write,
            patch('pathlib.Path.read_text') as mock_read,
        ):
            mock_is_file.return_value = True
            mock_read.return_value = '4'

            sriov = Sriov(path)
            sriov.sriov_numvfs = '0'
            sriov.set_numvfs('4')

            # Should first write 0, then 4
            assert mock_write.call_args_list == [
                (('0',),),
                (('4',),),
            ]

    def test_read_numvfs(self) -> None:
        """Test reading number of VFs."""
        path = Path('/sys/class/infiniband/mlx5_0/device')
        with patch('pathlib.Path.is_file') as mock_is_file, patch('pathlib.Path.read_text') as mock_read:
            mock_is_file.return_value = True
            mock_read.return_value = '4'

            sriov = Sriov(path)
            assert sriov.read_numvfs() == '4'

            mock_is_file.return_value = False
            assert sriov.read_numvfs() is None


class TestRdmaDevice:
    """Test RdmaDevice class."""

    def test_init(self) -> None:
        """Test device initialization."""
        with (
            patch('pathlib.Path.iterdir') as mock_iterdir,
            patch('pathlib.Path.is_file') as mock_is_file,
            patch('pathlib.Path.is_dir') as mock_is_dir,
            patch('pathlib.Path.resolve') as mock_resolve,
        ):
            # Mock device files
            mock_file = create_mock_file('fw_ver', '16.29.1120')
            mock_iterdir.return_value = [mock_file]
            mock_is_file.return_value = True
            mock_is_dir.return_value = True
            mock_resolve.return_value = Path('/sys/devices/pci0000:00/0000:00:02.0/mlx5_0')

            device = RdmaDevice(ibdev='mlx5_0')
            assert device.ibdev == 'mlx5_0'

    def test_get_ports(self) -> None:
        """Test getting all ports."""
        with (
            patch('pathlib.Path.iterdir') as mock_iterdir,
            patch('pathlib.Path.is_file') as mock_is_file,
            patch('pathlib.Path.is_dir') as mock_is_dir,
            patch('pathlib.Path.resolve') as mock_resolve,
        ):
            mock_port = create_mock_file('1', '')
            mock_iterdir.side_effect = [
                [],  # Device files
                [mock_port],  # Ports
                [],  # Port files
            ]
            mock_is_file.return_value = True
            mock_is_dir.return_value = True
            mock_resolve.return_value = Path('/sys/devices/pci0000:00/0000:00:02.0/mlx5_0')

            device = RdmaDevice(ibdev='mlx5_0')
            ports = device.get_ports()
            assert ports is not None
            assert len(ports) == 1
            assert ports[0].name == '1'

    def test_get_port(self) -> None:
        """Test getting port by number."""
        with (
            patch('pathlib.Path.iterdir') as mock_iterdir,
            patch('pathlib.Path.is_file') as mock_is_file,
            patch('pathlib.Path.is_dir') as mock_is_dir,
            patch('pathlib.Path.resolve') as mock_resolve,
        ):
            mock_iterdir.side_effect = [
                [],  # Device files
                [],  # Ports
                [],  # Port files
            ]
            mock_is_file.return_value = True
            mock_is_dir.return_value = True
            mock_resolve.return_value = Path('/sys/devices/pci0000:00/0000:00:02.0/mlx5_0')

            device = RdmaDevice(ibdev='mlx5_0')
            port = device.get_port('1')
            assert port is not None
            assert port.name == '1'
