# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Test string manipulation utilities.

This module tests string manipulation utilities:
- String conversion
- String formatting
- String validation
"""

from __future__ import annotations

import pytest

from sts.utils.string_extras import none_to_empty


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (None, ''),  # None becomes empty string
        ('', ''),  # Empty string stays empty
        ('test', 'test'),  # Non-empty string stays unchanged
        ('  ', '  '),  # Whitespace string stays unchanged
        ('None', 'None'),  # String 'None' stays unchanged
    ],
)
def test_none_to_empty(value: str | None, expected: str) -> None:
    """Test none_to_empty function.

    Args:
        value: Input value
        expected: Expected output
    """
    assert none_to_empty(value) == expected
