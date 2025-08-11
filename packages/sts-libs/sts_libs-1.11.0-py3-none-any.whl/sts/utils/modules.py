# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Kernel module management.

This module provides functionality for managing kernel modules:
- Module loading/unloading
- Module information
- Module dependencies
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sts.utils.cmdline import run
from sts.utils.errors import ModuleInUseError

DEFAULT_TIMEOUT = 5


@dataclass
class ModuleInfo:
    """Kernel module information.

    This class provides functionality for managing module information:
    - Module metadata
    - Module parameters
    - Module dependencies

    Args:
        name: Module name (optional, discovers first loaded module)
        size: Module size (optional, discovered from module)
        used_by: List of modules using this module (optional, discovered from module)
        state: Module state (optional, discovered from module)
        parameters: Module parameters (optional, discovered from module)

    Example:
        ```python
        info = ModuleInfo()  # Discovers first loaded module
        info = ModuleInfo(name='dm_mod')  # Discovers other values
        ```
    """

    # Optional parameters
    name: str | None = None
    size: int | None = None
    used_by: list[str] = field(default_factory=list)
    state: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize module information.

        Discovers module information based on provided parameters.
        """
        # If no name provided, get first loaded module
        if not self.name:
            try:
                line = Path('/proc/modules').read_text().splitlines()[0]
                self.name = line.split()[0]
            except (OSError, IndexError):
                return

        # Get module information if name is available
        if self.name:
            try:
                for line in Path('/proc/modules').read_text().splitlines():
                    parts = line.split(maxsplit=4)
                    if parts[0] == self.name:
                        self.size = int(parts[1])
                        self.state = parts[2]
                        if parts[3] != '-':
                            self.used_by = parts[3].rstrip(',').split(',')
                        break
            except (OSError, IndexError, ValueError):
                logging.warning(f'Failed to get module info for {self.name}', exc_info=True)

            # Get module parameters
            param_path = Path('/sys/module') / self.name / 'parameters'
            if param_path.is_dir():
                try:
                    for param in param_path.iterdir():
                        if param.is_file():
                            self.parameters[param.name] = param.read_text().strip()
                except OSError:
                    logging.warning(f'Failed to get parameters for {self.name}', exc_info=True)

    @property
    def exists(self) -> bool:
        """Check if module exists.

        Returns:
            True if exists, False otherwise

        Example:
            ```python
            info = ModuleInfo(name='dm_mod')
            info.exists
            True
            ```
        """
        if self.name:
            return run(f'modinfo {self.name} -n').succeeded
        return False

    @property
    def loaded(self) -> bool:
        """Check if module is loaded.

        Returns:
            True if loaded, False otherwise

        Example:
            ```python
            info = ModuleInfo(name='dm_mod')
            info.loaded
            True
            ```
        """
        return bool(self.state)

    def load(self, parameters: str | None = None) -> bool:
        """Load module.

        Args:
            parameters: Module parameters

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            info = ModuleInfo(name='dm_mod')
            info.load()
            True
            ```
        """
        if not self.name:
            logging.error('Module name required')
            return False

        cmd = ['modprobe', self.name]
        if parameters:
            cmd.append(parameters)

        result = run(' '.join(cmd))
        if result.failed:
            logging.error(f'Failed to load module: {result.stderr}')
            return False

        # Update module information
        self.__post_init__()
        return True

    def unload(self) -> bool:
        """Unload module.

        Returns:
            True if successful, False otherwise

        Raises:
            ModuleInUseError: If module is in use
            RuntimeError: If module cannot be unloaded

        Example:
            ```python
            info = ModuleInfo(name='dm_mod')
            info.unload()
            True
            ```
        """
        if not self.name:
            logging.error('Module name required')
            return False

        result = run(f'modprobe -r {self.name}')
        if result.failed:
            if f'modprobe: FATAL: Module {self.name} is in use.' in result.stderr:
                raise ModuleInUseError(self.name)
            raise RuntimeError(result.stderr)

        # Update module information
        self.__post_init__()
        return True

    def unload_with_dependencies(self) -> bool:
        """Unload module and its dependencies.

        Returns:
            True if successful, False otherwise

        Raises:
            ModuleInUseError: If module is in use
            RuntimeError: If module cannot be unloaded

        Example:
            ```python
            info = ModuleInfo(name='dm_mod')
            info.unload_with_dependencies()
            True
            ```
        """
        if not self.name:
            logging.error('Module name required')
            return False

        if self.used_by:
            logging.info(f'Removing modules dependent on {self.name}')
            for module in self.used_by:
                if (info := ModuleInfo(name=module)) and not info.unload_with_dependencies():
                    logging.error('Failed to unload dependent modules')
                    return False

        return self.unload()

    @classmethod
    def from_name(cls, name: str) -> ModuleInfo | None:
        """Get module information by name.

        Args:
            name: Module name

        Returns:
            Module information or None if not found

        Example:
            ```python
            info = ModuleInfo.from_name('dm_mod')
            info.used_by
            ['dm_mirror', 'dm_log']
            ```
        """
        info = cls(name=name)
        return info if info.exists else None


class ModuleManager:
    """Module manager functionality.

    This class provides functionality for managing kernel modules:
    - Module loading/unloading
    - Module information
    - Module dependencies

    Example:
        ```python
        mm = ModuleManager()
        mm.load('dm_mod')
        True
        ```
    """

    def __init__(self) -> None:
        """Initialize module manager."""
        self.modules_path = Path('/proc/modules')
        self.parameters_path = Path('/sys/module')

    def get_all(self) -> list[ModuleInfo]:
        """Get list of all loaded modules.

        Returns:
            List of module information

        Example:
            ```python
            mm = ModuleManager()
            mm.get_all()
            [ModuleInfo(name='dm_mod', ...), ModuleInfo(name='ext4', ...)]
            ```
        """
        modules = []
        try:
            for line in self.modules_path.read_text().splitlines():
                parts = line.split(maxsplit=4)
                info = ModuleInfo(name=parts[0])
                if info.exists:
                    modules.append(info)
        except (OSError, IndexError):
            logging.exception('Failed to get module list')
            return []

        return modules

    def get_parameters(self, name: str) -> dict[str, str]:
        """Get module parameters.

        Args:
            name: Module name

        Returns:
            Dictionary of parameter names and values

        Example:
            ```python
            mm = ModuleManager()
            mm.get_parameters('dm_mod')
            {'major': '253'}
            ```
        """
        if info := ModuleInfo(name=name):
            return info.parameters
        return {}

    def load(self, name: str, parameters: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Load module.

        Args:
            name: Module name
            parameters: Module parameters
            timeout: Maximum time to wait for module to load (seconds)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            mm = ModuleManager()
            mm.load('dm_mod')
            True
            mm.load('target_core_mod', timeout=1)
            True
            ```
        """
        info = ModuleInfo(name=name)
        if info.loaded:
            return True

        success = info.load(parameters)

        # Wait for module to be fully loaded
        return success and self._wait_for_module_state(name, expected_state=True, timeout=timeout)

    def unload(self, name: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Unload module.

        Args:
            name: Module name
            timeout: Maximum time to wait for module to unload (seconds)

        Returns:
            True if successful, False otherwise

        Raises:
            ModuleInUseError: If module is in use
            RuntimeError: If module cannot be unloaded

        Example:
            ```python
            mm = ModuleManager()
            mm.unload('dm_mod')
            True
            mm.unload('target_core_mod', timeout=10)
            True
            ```
        """
        info = ModuleInfo(name=name)
        if not info.loaded:
            return True

        success = info.unload()

        # Wait for module to be fully unloaded
        return success and self._wait_for_module_state(name, expected_state=False, timeout=timeout)

    def unload_with_dependencies(self, name: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Unload module and its dependencies.

        Args:
            name: Module name
            timeout: Maximum time to wait for module to unload (seconds)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            mm = ModuleManager()
            mm.unload_with_dependencies('dm_mod')
            True
            mm.unload_with_dependencies('target_core_mod', timeout=10)
            True
            ```
        """
        info = ModuleInfo(name=name)
        if not info.loaded:
            return True

        success = info.unload_with_dependencies()

        # Wait for module to be fully unloaded
        return success and self._wait_for_module_state(name, expected_state=False, timeout=timeout)

    def _wait_for_module_state(self, module_name: str, *, expected_state: bool, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Wait for module to reach expected state with timeout.

        Args:
            module_name: Name of the module to check
            expected_state: If True, wait for module to be loaded; if False, wait for unloaded
            timeout: Maximum time to wait in seconds

        Returns:
            True if module reached expected state within timeout, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            info = ModuleInfo(name=module_name)
            current_state = info.loaded
            if current_state == expected_state:
                return True
            time.sleep(0.1)  # Poll every 100ms
        return False
