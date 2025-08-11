# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Snapm - Linux snapshot manager.

This package provides functionality for managing snapm.
"""

from __future__ import annotations

from sts.snapm.base import SnapmBase
from sts.snapm.plugin import Plugin, PluginManager
from sts.snapm.snapset import Snapset, SnapsetInfo
from sts.snapm.snapshot import Snapshot, SnapshotInfo

__all__ = [
    'Plugin',
    'PluginManager',
    'SnapmBase',
    'Snapset',
    'SnapsetInfo',
    'Snapshot',
    'SnapshotInfo',
]
