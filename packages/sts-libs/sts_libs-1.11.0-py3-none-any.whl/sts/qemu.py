# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""QEMU disk image management.

This module provides functionality for managing QEMU disk images:
- Image creation and deletion
- Format selection and options
- Storage allocation strategies

QEMU Image Formats:
1. qcow2 (QEMU Copy-On-Write v2):
   - Space-efficient (allocates on write)
   - Supports snapshots
   - Backing files for base images
   - Optional encryption
   - Performance features (compat levels)

2. raw:
   - Direct disk image
   - Best performance
   - Fixed size allocation
   - No advanced features

3. Other formats:
   - vmdk (VMware)
   - vdi (VirtualBox)
   - vhdx (Hyper-V)
   - qed (deprecated)
"""

from __future__ import annotations

import logging
from pathlib import Path

from sts.utils.cmdline import run
from sts.utils.packages import Dnf

# Supported options for qcow2 format
QCOW_OPTIONS = [
    'compat',  # Compatibility level (0.10/1.1)
    'backing_file',  # Base image for COW
    'encryption',  # Enable encryption
    'cluster_size',  # Allocation unit size
    'preallocation',  # Space allocation strategy
    'lazy_refcounts',  # Performance vs safety trade-off
]


def create_image(
    name: str,
    *,
    size: str = '1024',
    fmt: str | None = None,
    path: str | Path = '/var/tmp',
    **options: str,
) -> bool:
    """Create disk image.

    Creates a new disk image with specified format and options:
    - qcow2: Efficient, feature-rich format
    - raw: Simple, high-performance format
    - Other formats supported by qemu-img

    Size can use suffixes:
    - K/k: Kilobytes (1024 bytes)
    - M/m: Megabytes (1024K)
    - G/g: Gigabytes (1024M)
    - T/t: Terabytes (1024G)

    qcow2 options:
    - compat: '0.10' or '1.1' (feature level)
    - backing_file: Path to base image
    - encryption: 'on' or 'off'
    - cluster_size: Power of 2 (default: 64K)
    - preallocation: 'off', 'metadata', 'falloc', 'full'
    - lazy_refcounts: 'on' or 'off'

    Args:
        name: Image name (without extension)
        size: Image size (default: 1024 bytes)
        fmt: Image format (default: raw)
        path: Output directory (default: /var/tmp)
        **options: Format-specific options

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        # Create 1GB qcow2 image with newer features
        create_image('test', size='1G', fmt='qcow2', compat='1.1')
        True
        # Create raw image with fixed allocation
        create_image('test', size='10G', fmt='raw')
        True
        ```
    """
    # Ensure qemu-img is installed
    pm = Dnf()
    if not pm.install('qemu-img'):
        return False

    # Build image path (always .img extension)
    img_path = Path(path) / f'{name}.img'

    # Build qemu-img command
    cmd = ['qemu-img', 'create']
    if fmt:
        cmd.extend(['-f', fmt])
        # Handle qcow2-specific options
        if fmt == 'qcow2' and options:
            opts = [f'{k}={v}' for k, v in options.items() if k in QCOW_OPTIONS]
            if opts:
                cmd.extend(['-o', ','.join(opts)])
    cmd.extend([str(img_path), size])

    # Create image using qemu-img
    result = run(' '.join(cmd))
    if result.failed:
        logging.error('Failed to create disk image')
        return False

    return True


def delete_image(name: str, path: str | Path = '/var/tmp') -> bool:
    """Delete disk image.

    Removes disk image file:
    - Handles missing files
    - Logs errors
    - Returns success status

    Note: Does not handle:
    - Mounted images
    - Images in use by VMs
    - Backing file cleanup

    Args:
        name: Image name (without extension)
        path: Image directory (default: /var/tmp)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        delete_image('test')  # Deletes /var/tmp/test.img
        True
        ```
    """
    img_path = Path(path) / f'{name}.img'
    try:
        img_path.unlink(missing_ok=True)
    except OSError:
        logging.exception(f'Failed to delete image: {img_path}')
        return False
    return True
