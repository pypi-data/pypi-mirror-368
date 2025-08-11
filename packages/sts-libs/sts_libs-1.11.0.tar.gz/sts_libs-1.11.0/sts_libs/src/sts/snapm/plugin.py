# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Snapshot Manager plugin functionality.

This module provides functionality for managing Snapshot Manager plugins:
- Plugin discovery
- Plugin information retrieval
- Plugin configuration
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from sts.snapm.base import SnapmBase, SnapmOptions

if TYPE_CHECKING:
    from sts.utils.cmdline import CommandResult


class Plugin:
    """Snapshot Manager plugin.

    Represents a plugin that provides snapshot functionality:
    - Plugin name
    - Plugin version
    - Plugin type

    Args:
        name: Plugin name (e.g., "lvm2-cow", "lvm2-thin")
        version: Plugin version (e.g., "0.1.0")
        plugin_type: Plugin type (e.g., "Lvm2CowSnapshot", "Lvm2ThinSnapshot")
    """

    def __init__(
        self,
        name: str,
        version: str = '',
        plugin_type: str = '',
    ) -> None:
        """Initialize plugin.

        Args:
            name: Plugin name (e.g., "lvm2-cow", "lvm2-thin")
            version: Plugin version (e.g., "0.1.0")
            plugin_type: Plugin type (e.g., "Lvm2CowSnapshot", "Lvm2ThinSnapshot")

        Examples:
            ```python
            # Create a plugin with basic information
            plugin = Plugin(name='lvm2-cow')

            # Create a plugin with full details
            plugin = Plugin(
                name='lvm2-thin',
                version='0.1.0',
                plugin_type='Lvm2ThinSnapshot',
            )
            ```
        """
        self.name = name
        self.version = version
        self.plugin_type = plugin_type

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Plugin:
        """Create plugin from dictionary.

        Args:
            data: Dictionary data from snapm plugin report

        Returns:
            Plugin instance

        Examples:
            ```python
            # Parse plugin data from JSON
            plugin_data = {
                'plugin_name': 'lvm2-cow',
                'plugin_version': '0.1.0',
                'plugin_type': 'Lvm2CowSnapshot',
            }
            plugin = Plugin.from_dict(plugin_data)
            ```
        """
        return cls(
            name=data.get('plugin_name', ''),
            version=data.get('plugin_version', ''),
            plugin_type=data.get('plugin_type', ''),
        )


@dataclass
class PluginManager(SnapmBase):
    """Plugin management.

    Manages Snapshot Manager plugins:
    - Lists available plugins
    - Provides plugin information
    - Helps select appropriate plugin for sources

    Examples:
        List all plugins:
        ```python
        manager = PluginManager()
        plugins = manager.list_plugins()
        ```

        Get plugin details:
        ```python
        manager = PluginManager()
        all_plugins = manager.get_plugins()
        for plugin in all_plugins:
            print(f'{plugin.name}: {plugin.version} (Type: {plugin.plugin_type})')
        ```
    """

    # Class-level constants
    SUBCOMMAND: ClassVar[str] = 'plugin'

    def list_plugins(self, *, fields: str | None = None, json_output: bool = False) -> CommandResult:
        """List all plugins.

        Lists available plugins:
        - Shows basic information
        - Can select custom fields
        - Optional JSON output

        Args:
            fields: Comma-separated list of fields to display
                   Example: "plugin_name,plugin_version,plugin_type"
            json_output: Whether to output in JSON format

        Returns:
            Command result with list output

        Examples:
            ```python
            # Simple list
            manager = PluginManager()
            result = manager.list_plugins()
            print(result.stdout)

            # Custom fields
            result = manager.list_plugins(fields='plugin_name,plugin_version')
            print(result.stdout)

            # JSON output for programmatic use
            result = manager.list_plugins(json_output=True)
            import json

            plugins_data = json.loads(result.stdout)
            for plugin in plugins_data.get('Plugins', []):
                print(f'{plugin["plugin_name"]}: {plugin["plugin_version"]}')
            ```
        """
        options: SnapmOptions = {}

        # Add fields if provided
        if fields:
            options['--options'] = fields

        # Add JSON output if requested
        if json_output:
            options['--json'] = None

        return self.run_command(subcommand=self.SUBCOMMAND, action='list', options=options)

    def get_plugins(self) -> list[Plugin]:
        """Get all available plugins.

        Retrieves information about all plugins:
        - Lists all plugins in system
        - Creates Plugin instances

        Returns:
            List of Plugin instances

        Note:
            Logs an error message if plugin retrieval fails

        Examples:
            ```python
            # Get all plugins
            manager = PluginManager()
            try:
                plugins = manager.get_plugins()
                for plugin in plugins:
                    print(f'{plugin.name}: {plugin.version} (Type: {plugin.plugin_type})')
            except Exception as e:
                print(f'Failed to get plugins: {e}')

            # Find plugins of a specific type
            plugins = manager.get_plugins()
            cow_plugins = [p for p in plugins if 'Lvm2CowSnapshot' == p.plugin_type]
            ```
        """
        plugins: list[Plugin] = []

        # Get plugin list in JSON format for easier parsing
        result = self.list_plugins(json_output=True)

        if result.failed:
            logging.error(f'Failed to list plugins: {result.stderr}')
            return plugins

        if not result.stdout:
            return plugins

        try:
            # Parse JSON output
            data = json.loads(result.stdout)

            # Extract plugins from the 'Plugins' key
            if isinstance(data, dict):
                items = data.get('Plugins', [])
            elif isinstance(data, list):
                items = data
            else:
                logging.warning(f'Unexpected plugin data structure: {data}')
                return plugins

            # Create plugin instances from each entry
            for item in items:
                plugin = Plugin.from_dict(item)
                plugins.append(plugin)

        except json.JSONDecodeError as e:
            logging.warning(f'Failed to parse plugins (invalid JSON): {e}')
        except (TypeError, ValueError) as e:
            logging.warning(f'Failed to process plugin data: {e}')

        return plugins
