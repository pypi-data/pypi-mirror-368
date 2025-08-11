# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Version handling utilities.

This module provides functionality for managing software versions:
- Version parsing and representation
- Version comparison operations
- Version validation and normalization
"""

from __future__ import annotations

import re
from typing import NamedTuple


class VersionInfo(NamedTuple):
    """A named tuple representing a software version with major, minor, micro, patch, and build components.

    This class provides functionality for version representation and comparison:
    - Semantic version parsing (e.g., '1.2.3', '1.2.3-456', '8.2.6.3-166')
    - Version comparison operations
    - String representation

    Args:
        major: Major version component (required)
        minor: Minor version component (optional, defaults to 0)
        micro: Micro version component (optional, defaults to 0)
        patch: Patch version component (optional, defaults to 0)
        build: Build version component (optional, comes after hyphen, defaults to 0)

    Example:
        ```python
        version = VersionInfo(8, 2, 6, 3, 166)  # major=8, minor=2, micro=6, patch=3, build=166
        version = VersionInfo(1, 2, 3, 0, 456)  # major=1, minor=2, micro=3, patch=0, build=456
        version = VersionInfo(1, 2, 3)  # patch and build default to 0
        version = VersionInfo(1, 2)  # micro, patch, and build default to 0
        version = VersionInfo(1)  # minor, micro, patch, and build default to 0
        ```
    """

    major: int
    minor: int = 0
    micro: int = 0
    patch: int = 0
    build: int = 0

    @classmethod
    def from_string(cls, version_string: str) -> VersionInfo:
        """Parse a version string into a VersionInfo tuple.

        Parses version strings in the format 'major.minor.micro[-build]' where
        any component after major is optional. Build number comes after hyphen.

        Args:
            version_string: Version string to parse (e.g., '1.2.3', '1.2.3-456', '8.2.6.3-166')

        Returns:
            VersionInfo: Parsed version tuple

        Raises:
            ValueError: If the version string is empty or invalid
            ValueError: If any version component is not a valid integer

        Example:
            ```python
            version = VersionInfo.from_string('8.2.6.3-166')  # major=8, minor=2, micro=6, build=166
            version = VersionInfo.from_string('1.2.3-456')  # major=1, minor=2, micro=3, build=456
            version = VersionInfo.from_string('1.2.3')  # major=1, minor=2, micro=3, build=0
            version = VersionInfo.from_string('1.2')  # major=1, minor=2, micro=0, build=0
            version = VersionInfo.from_string('1')  # major=1, minor=0, micro=0, build=0
            ```
        """
        if not version_string or not version_string.strip():
            raise ValueError('Version string cannot be empty')

        version_string = version_string.strip()

        # Check for supported format
        if not cls._is_valid_format(version_string):
            raise ValueError(
                f'Unsupported version format: "{version_string}". Expected format: "major[.minor[.micro]][-build]"'
            )

        # Split on hyphen first to separate build number
        hyphen_parts = version_string.split('-')
        main_version = hyphen_parts[0]
        build = int(hyphen_parts[1]) if len(hyphen_parts) > 1 else 0

        parts = main_version.split('.')

        # Ensure we have at least a major version
        if len(parts) < 1 or not parts[0]:
            raise ValueError('Version string must contain at least a major version')

        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        micro = int(parts[2]) if len(parts) > 2 and parts[2] else 0
        patch = int(parts[3]) if len(parts) > 3 and parts[3] else 0

        # Ensure all components are non-negative
        if any(component < 0 for component in [major, minor, micro, patch, build]):
            raise ValueError('Version components must be non-negative integers')

        return cls(major=major, minor=minor, micro=micro, patch=patch, build=build)

    @staticmethod
    def _is_valid_format(version_string: str) -> bool:
        """Check if version string follows supported format.

        Supported format: major[.minor[.micro[.patch]]][-build]
        - Each component must be a non-negative integer
        - Maximum 4 dot-separated components plus optional build after hyphen
        - No consecutive dots
        - Cannot start or end with dots
        - Only digits, dots, and single hyphen allowed
        - If hyphen is present, build must be a non-negative integer

        Args:
            version_string: Version string to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        # Split on hyphen to check build part
        hyphen_parts = version_string.split('-')

        # Can have at most one hyphen
        if len(hyphen_parts) > 2:
            return False

        main_version = hyphen_parts[0]
        build_part = hyphen_parts[1] if len(hyphen_parts) > 1 else None

        # Validate main version part (major.minor.micro.patch)
        pattern = r'^[0-9]+(\.[0-9]+){0,3}$'
        if not re.match(pattern, main_version):
            return False

        # Check main version components
        parts = main_version.split('.')
        if len(parts) > 4:  # Maximum 4 components
            return False

        # Validate build part if present
        return build_part is None or build_part.isdigit()
