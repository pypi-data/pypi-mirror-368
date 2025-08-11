# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Managing configuration files.

The `Config` class supports loading, modifying, and saving configuration files in a key-value format.
It handles comments and preserves the original file structure when saving changes.

The config file looks like:
Auth.ReplayWindow = 2m
Auth.TimeStampJitter = 1s

Key features:
- Loading configuration from a file with support for comments and key-value pairs.
- Setting and getting individual configuration parameters.
- Saving updated configuration back to the file while maintaining comments and formatting.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Config:
    """Base configuration class for managing configuration files."""

    def __init__(self, config_path: Path) -> None:
        """Initialize configuration.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.parameters: dict[str, str] = {}
        if self.config_path.exists():
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file.

        Parses configuration format:
        - Key = Value pairs
        - Comments start with #
        - Whitespace ignored
        """
        try:
            lines = self.config_path.read_text().splitlines()
            for line in lines:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#') and '=' in stripped_line:
                    key, value = map(str.strip, stripped_line.split('=', 1))
                    self.parameters[key] = value
        except OSError:
            logging.exception('Failed to load config')

    def set_parameters(self, parameters: dict[str, str]) -> None:
        """Set configuration parameters.

        Updates multiple parameters at once:
        - Overwrites existing values
        - Adds new parameters

        Args:
            parameters: Dictionary of parameter names and values
        """
        self.parameters.update(parameters)

    def get_parameter(self, name: str) -> str | None:
        """Get parameter value.

        Args:
            name: Parameter name

        Returns:
            Parameter value if found, None otherwise
        """
        return self.parameters.get(name)

    def save(self) -> bool:
        """Save configuration to file.

        Preserves file format:
        - Keeps comments
        - Maintains spacing
        - Updates values

        Returns:
            True if successful, False otherwise
        """
        try:
            lines = self.config_path.read_text().splitlines() if self.config_path.exists() else []
            updated_lines = []

            for line in lines:
                if line.strip().startswith('#') or '=' not in line:
                    updated_lines.append(line)
                    continue

                key = line.split('=', 1)[0].strip()
                if key in self.parameters:
                    updated_lines.append(f'{key} = {self.parameters[key]}')
                    del self.parameters[key]
                else:
                    updated_lines.append(line)

            for key, value in self.parameters.items():
                updated_lines.append(f'{key} = {value}')

            self.config_path.write_text('\n'.join(updated_lines) + '\n')
        except OSError:
            logging.exception('Failed to save config')
            return False
        return True
