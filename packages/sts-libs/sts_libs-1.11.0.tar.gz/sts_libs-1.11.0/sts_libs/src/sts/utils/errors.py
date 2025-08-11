# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Storage Test Suite error classes.

This module provides a hierarchy of error classes used across the project:

Base Classes:
- STSError: Base class for all STS exceptions
- DeviceError: Base class for device-related errors
- ModuleError: Base class for kernel module errors
- PackageError: Base class for package-related errors
- SysError: Base class for system-related errors

Device Errors:
- DeviceNotFoundError: Device does not exist
- DeviceTypeError: Device is not of expected type

Module Errors:
- ModuleLoadError: Failed to load kernel module
- ModuleUnloadError: Failed to unload kernel module
- ModuleInUseError: Module cannot be unloaded because it is in use

Package Errors:
- PackageNotFoundError: Package does not exist
- PackageInstallError: Failed to install package

System Errors:
- SysNotSupportedError: Operation not supported on this system
"""

from __future__ import annotations


class STSError(Exception):
    """Base class for all STS exceptions."""


class DeviceError(STSError):
    """Base class for device-related errors."""


class DeviceNotFoundError(DeviceError):
    """Device does not exist."""


class DeviceTypeError(DeviceError):
    """Device is not of expected type."""


class ModuleError(STSError):
    """Base class for kernel module errors."""


class ModuleLoadError(ModuleError):
    """Failed to load kernel module."""


class ModuleUnloadError(ModuleError):
    """Failed to unload kernel module."""


class ModuleInUseError(ModuleError):
    """Module cannot be unloaded because it is in use."""


class PackageError(STSError):
    """Base class for package-related errors."""


class PackageNotFoundError(PackageError):
    """Package does not exist."""


class PackageInstallError(PackageError):
    """Failed to install package."""


class SysError(STSError):
    """Base class for system-related errors."""


class SysNotSupportedError(SysError):
    """Operation not supported on this system."""
