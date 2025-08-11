# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from os import getenv
from typing import ClassVar

import pytest

from sts import lvm


class TestVDO:
    lv_name: str = getenv('VDO_LV_NAME', 'vdolv')
    pool_name: str = getenv('VDO_POOL_NAME', 'vdopool0')
    size: str = getenv('VDO_SIZE', '8G')
    vdo_prefix: str = 'vdo_'
    vdo_use_prefix: str = 'vdo_use_'
    allocation_prefix: str = 'allocation/'
    slab_size_default: str = 'vdo_slab_size_mb=128'

    simple_valid_cases: ClassVar[dict[str, tuple[int, ...]]] = {
        'minimum_io_size': (512, 4096),
        'block_map_cache_size_mb': (
            128,
            4096,
        ),  # 65536, 16777215 From 128 MiB to below 16 TiB
        'block_map_period': (1, 8192, 16380),
        'sparse_index': (0, 1),
        'index_memory_size_mb': (256, 1024),  # 1048576  # From 256 MiB to 1 TiB
        'slab_size_mb': (128, 1024, 2048),  # 32768 # Power of two between 128 MiB and 32 GiB (need 34G dev minimum)
        'ack_threads': (0, 1, 50, 100),
        'bio_threads': (1, 4, 50, 100),
        'bio_rotation': (1, 64, 1024),
        'cpu_threads': (1, 2, 50, 100),
        'hash_zone_threads': (1, 50, 100),  # 0 or [1-100]
        'logical_threads': (1, 8),  # 0 or [1-60]
        'physical_threads': (1, 5),  # 0 or [1-16]
        'max_discard': (1, 1500, (2**32 // 4096) - 1),  # Min to max UINT_MAX/4096
        'pool_header_size': (512, 1024, 2048),
    }

    valid_cases: ClassVar[tuple[tuple[str, ...], ...]] = (
        ('logical_threads=0', 'hash_zone_threads=0', 'physical_threads=0'),
        ('logical_threads=5', 'hash_zone_threads=5', 'physical_threads=5', 'slab_size_mb=128'),
        (
            'logical_threads=60',
            'hash_zone_threads=100',
            'physical_threads=8',
            'slab_size_mb=128',
            'block_map_cache_size_mb=1024',
        ),
        # ('logical_threads=60', 'hash_zone_threads=100', 'physical_threads=8', 'slab_size_mb=128',
        # 'ack_threads=100', 'bio_threads=100', 'cpu_threads=100', 'block_map_cache_size_mb=1024'),
        ('logical_threads=60', 'block_map_cache_size_mb=1024'),
    )

    @pytest.mark.usefixtures('_vdo_test', 'setup_vg')
    def test_vdo_create(self, setup_vg: str) -> None:
        vg_name = setup_vg
        lv = lvm.LogicalVolume(name=self.lv_name, vg=vg_name)

        def _test_vdo_create(option: str, option_string: str) -> None:
            assert lv.create(type='vdo', vdopool=self.pool_name, size=self.size, **{option: f'"{option_string}"'})
            # assert f'ack {value}' in lvm.run(f'dmsetup table {vg_name}-vpool0-vpool').stdout
            # logging.info(lvm._run(f'dmsetup table {vg_name}-{self.pool_name}-vpool').stdout)
            assert lv.remove()

        for case in self.simple_valid_cases:
            if case not in ('minimum_io_size', 'pool_header_size'):
                for value in self.simple_valid_cases[case]:
                    _test_vdo_create(option='vdosettings', option_string=f'{self.slab_size_default} {case}={value}')
                    # Test vdo setting with vdo_ prefix
                    prefix = self.vdo_prefix
                    if case == 'sparse_index':
                        prefix = self.vdo_use_prefix
                    _test_vdo_create(
                        option='vdosettings', option_string=f'{self.slab_size_default} {prefix}{case}={value}'
                    )
                    _test_vdo_create(
                        option='config',
                        option_string=(
                            f'{self.allocation_prefix}{self.slab_size_default} '
                            f'{self.allocation_prefix}{prefix}{case}={value}'
                        ),
                    )

        for v_case in self.valid_cases:
            _test_vdo_create(option='--vdosettings', option_string=' '.join(v_case))
            # sparse_index needs vdo_use_prefix
            _test_vdo_create(
                option='--vdosettings',
                option_string=' '.join([f'{self.vdo_prefix}{x}' for x in v_case if 'sparse_index' not in x]),
            )
            _test_vdo_create(
                option='--config',
                option_string=' '.join(
                    [f'{self.allocation_prefix}{self.vdo_prefix}{x}' for x in v_case if 'sparse_index' not in x]
                ),
            )

    @pytest.mark.usefixtures('setup_vg')
    def test_vdo_change(self, setup_vg: str) -> None:
        vg_name = setup_vg
        lv = lvm.LogicalVolume(name=self.lv_name, vg=vg_name, pool_name=self.pool_name)

        def _test_lv_change(vdosettings_string: str) -> None:
            assert lv.change('-an', f'{vg_name}/{self.lv_name}')
            assert lv.change('-an', f'{vg_name}/{self.pool_name}')
            assert lv.change(f'{vg_name}/{self.pool_name}', vdosettings=f'{vdosettings_string}')
            # assert f'ack {value}' in lvm.run(f'dmsetup table {vg_name}-vpool0-vpool').stdout
            assert lv.change('-ay', f'{vg_name}/{self.pool_name}')
            assert lv.change('-ay', f'{vg_name}/{self.lv_name}')
            logging.info(lvm.run(f'dmsetup table {vg_name}-{self.pool_name}-vpool').stdout)

        assert lv.create(
            type='vdo',
            vdopool=self.pool_name,
            size=self.size,
            vdosettings=self.slab_size_default,
        )
        for case in self.simple_valid_cases:
            if case not in (
                'minimum_io_size',
                'pool_header_size',
                'sparse_index',
                'index_memory_size_mb',
                'slab_size_mb',
            ):
                for value in self.simple_valid_cases[case]:
                    _test_lv_change(vdosettings_string=f'{case}={value}')
                    # Test vdo setting with vdo_ prefix
                    _test_lv_change(vdosettings_string=f'{self.vdo_prefix}{case}={value}')
        assert lv.remove()
