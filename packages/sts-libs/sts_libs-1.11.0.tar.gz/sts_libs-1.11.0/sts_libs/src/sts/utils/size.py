# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Size conversion utilities.

This module provides functionality for converting between human-readable sizes and bytes:
- Human to bytes conversion (e.g., '1KiB' -> 1024)
- Bytes to human conversion (e.g., 1024 -> '1KiB')
- Size validation
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final

# Size units
BYTE: Final[int] = 1
KIB: Final[int] = 1024
MIB: Final[int] = KIB * 1024
GIB: Final[int] = MIB * 1024
TIB: Final[int] = GIB * 1024
PIB: Final[int] = TIB * 1024
EIB: Final[int] = PIB * 1024
ZIB: Final[int] = EIB * 1024
YIB: Final[int] = ZIB * 1024


class Unit(str, Enum):
    """Size units."""

    B = 'B'
    KIB = 'KiB'
    MIB = 'MiB'
    GIB = 'GiB'
    TIB = 'TiB'
    PIB = 'PiB'
    EIB = 'EiB'
    ZIB = 'ZiB'
    YIB = 'YiB'


@dataclass
class Size:
    """Size representation.

    This class provides functionality for size operations:
    - Size parsing
    - Unit conversion
    - String representation

    Args:
        value: Size value (optional, defaults to 0)
        unit: Size unit (optional, defaults to bytes)

    Example:
        ```python
        size = Size()  # Zero bytes
        size = Size(1024)  # 1024 bytes
        size = Size(1.0, Unit.KIB)  # Custom value and unit
        size = Size.from_string('1KiB')  # From string
        ```
    """

    # Optional parameters with defaults
    value: float = 0.0
    unit: Unit = Unit.B

    # Regular expression for parsing human-readable sizes
    SIZE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r'^([\-0-9\.]+)(Ki|Mi|Gi|Ti|Pi|Ei|Zi|Yi)?B$',
    )

    # Unit multipliers (powers of 1024)
    MULTIPLIERS: ClassVar[dict[Unit, int]] = {
        Unit.B: BYTE,
        Unit.KIB: KIB,
        Unit.MIB: MIB,
        Unit.GIB: GIB,
        Unit.TIB: TIB,
        Unit.PIB: PIB,
        Unit.EIB: EIB,
        Unit.ZIB: ZIB,
        Unit.YIB: YIB,
    }

    def __post_init__(self) -> None:
        """Initialize size.

        Converts value to appropriate unit if needed.
        """
        # Convert to appropriate unit if value is large
        if self.unit == Unit.B and self.value >= KIB:
            bytes_ = int(self.value)
            value = float(bytes_)
            unit = Unit.B
            for next_unit in list(Unit)[1:]:  # Skip B
                if value < KIB:
                    break
                value /= 1024
                unit = next_unit
            self.value = value
            self.unit = unit

    @classmethod
    def from_string(cls, size: str) -> Size | None:
        """Parse size from string.

        Args:
            size: Size string (e.g., '1KiB')

        Returns:
            Size instance or None if invalid

        Example:
            ```python
            Size.from_string('1KiB')
            Size(value=1.0, unit=Unit.KIB)
            ```
        """
        if not size:
            return None

        # Handle pure numbers as bytes
        if size.isdigit():
            return cls(float(size), Unit.B)

        # Parse size with unit
        match = cls.SIZE_PATTERN.match(size)
        if not match:
            logging.error(f'Invalid size format: {size}')
            return None

        try:
            value = float(match.group(1))
            unit_str = match.group(2)
            unit = Unit.B if not unit_str else Unit(f'{unit_str}B')
            return cls(value, unit)
        except (ValueError, KeyError):
            logging.exception('Failed to parse size')
            return None

    def to_bytes(self) -> int:
        """Convert to bytes.

        Returns:
            Size in bytes

        Example:
            ```python
            Size(1.0, Unit.KIB).to_bytes()
            1024
            ```
        """
        return int(self.value * self.MULTIPLIERS[self.unit])

    @classmethod
    def from_bytes(cls, bytes_: int) -> Size:
        """Convert bytes to human-readable size.

        Args:
            bytes_: Size in bytes

        Returns:
            Size instance

        Example:
            ```python
            Size.from_bytes(1024)
            Size(value=1.0, unit=Unit.KIB)
            ```
        """
        if bytes_ < KIB:
            return cls(float(bytes_), Unit.B)

        value = float(bytes_)
        unit = Unit.B  # Default unit
        for next_unit in list(Unit)[1:]:  # Skip B
            if value < KIB:
                break
            value /= 1024
            unit = next_unit

        return cls(value, unit)

    def __str__(self) -> str:
        """Return human-readable string.

        Returns:
            Size string (e.g., '1KiB')

        Example:
            ```python
            str(Size(1.0, Unit.KIB))
            '1KiB'
            ```
        """
        # Remove decimal part if whole number
        if self.value.is_integer():
            return f'{int(self.value)}{self.unit}'
        return f'{self.value:.1f}{self.unit}'


def size_human_check(size: str) -> bool:
    """Check if size string is valid.

    Args:
        size: Size string to check

    Returns:
        True if valid, False otherwise

    Example:
        ```python
        size_human_check('1KiB')
        True
        ```
    """
    return Size.from_string(size) is not None


def size_human_2_size_bytes(size: str) -> int | None:
    """Convert human-readable size to bytes.

    Args:
        size: Size string (e.g., '1KiB')

    Returns:
        Size in bytes or None if invalid

    Example:
        ```python
        size_human_2_size_bytes('1KiB')
        1024
        ```
    """
    if size_obj := Size.from_string(size):
        return size_obj.to_bytes()
    return None


def size_bytes_2_size_human(bytes_: int | str | None) -> str | None:
    """Convert bytes to human-readable size.

    Args:
        bytes_: Size in bytes

    Returns:
        Human-readable size or None if invalid

    Example:
        ```python
        size_bytes_2_size_human(1024)
        '1KiB'
        ```
    """
    if not bytes_:
        return None

    try:
        size = Size.from_bytes(int(bytes_))
        return str(size)
    except (ValueError, TypeError):
        logging.exception('Invalid bytes value')
        return None
