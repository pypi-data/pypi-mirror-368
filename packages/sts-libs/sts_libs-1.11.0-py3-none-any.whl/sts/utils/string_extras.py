# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""String manipulation utilities.

This module provides utilities for string manipulation:
- String conversion
- String formatting
- String validation
"""

from __future__ import annotations

import random
import string


def rand_string(length: int = 8, chars: str | None = None) -> str:
    """Generate random string.

    Args:
        length: Length of string to generate
        chars: Characters to use for generation (default: ascii_lowercase + digits)

    Returns:
        Random string of specified length

    Example:
        ```python
        rand_string()
        'a1b2c3d4'
        rand_string(4)
        'w9x8'
        rand_string(4, 'ABC123')
        'B1CA'
        ```
    """
    chars = chars or string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def none_to_empty(value: str | None) -> str:
    """Convert None to empty string.

    Args:
        value: Value to convert

    Returns:
        Empty string if value is None, otherwise value

    Example:
        ```python
        none_to_empty(None)
        ''
        none_to_empty('test')
        'test'
        ```
    """
    return '' if value is None else value
