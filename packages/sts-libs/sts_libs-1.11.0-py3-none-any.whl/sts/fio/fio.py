# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""FIO test execution.

This module provides functionality for running FIO tests:
- Parameter management
- FIO file support
- Test execution
"""

from __future__ import annotations

import configparser
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sts.fio.errors import FIOConfigError, FIOExecutionError
from sts.fio.parameters import (
    BlockDeviceParameters,
    DefaultParameters,
    FileSystemParameters,
    FIOParameters,
    StressParameters,
)
from sts.utils.cmdline import run
from sts.utils.packages import ensure_installed


@dataclass
class FIO:
    """FIO test execution.

    This class provides functionality for running FIO tests:
    - Parameter management
    - FIO file support
    - Test execution

    Args:
        filename: Target file or device (optional, discovered from parameters)
        parameters: FIO parameters (optional, defaults to DefaultParameters)
        options: Additional FIO options (optional)
        config_file: FIO config file path (optional)

    Example:
        ```python
        fio = FIO()  # Uses default parameters
        fio = FIO('/dev/sda')  # Uses device with default parameters
        fio = FIO(parameters=DefaultParameters(name='test'))  # Custom parameters
        ```
    """

    # Optional parameters
    filename: str | Path | None = None
    parameters: FIOParameters | None = None
    options: list[str] = field(default_factory=list)
    config_file: str | Path | None = None

    def __post_init__(self) -> None:
        """Initialize FIO.

        Discovers filename from parameters if not provided.
        Loads parameters from config file if provided.
        Sets default parameters if none provided.

        Raises:
            FIOExecutionError: If FIO installation fails
        """
        # Install FIO
        ensure_installed('fio')

        # Convert filename to Path if provided
        if self.filename:
            self.filename = Path(self.filename)

        # Load parameters from config file if provided
        if self.config_file:
            self.load_config_file(self.config_file)
            # Get filename from parameters if not provided
            if not self.filename and self.parameters and hasattr(self.parameters, 'filename'):
                self.filename = self.parameters.filename

        # Set default parameters if none provided
        elif not self.parameters:
            self.parameters = DefaultParameters(name='sts-fio-default')
            # Get filename from parameters if not provided
            if not self.filename and hasattr(self.parameters, 'filename'):
                self.filename = self.parameters.filename

    def load_config_file(self, config_file: str | Path) -> None:
        """Load parameters from FIO config file.

        Args:
            config_file: Path to FIO config file

        Raises:
            FIOConfigError: If config file is invalid or cannot be read

        Example:
            ```python
            fio.load_config_file('test.fio')
            ```
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FIOConfigError(f'Config file not found: {config_path}')

        try:
            config = configparser.ConfigParser()
            config.read(config_path)

            # Get the first job section
            job_section = next(s for s in config.sections() if s != 'global')
            params = dict(config[job_section])

            # Convert parameters
            self.parameters = FIOParameters(
                name=job_section,
                **{k: v for k, v in params.items() if not k.startswith('_')},  # type: ignore[arg-type]
            )
        except (configparser.Error, StopIteration) as e:
            raise FIOConfigError(f'Invalid config file: {e}') from e

    def save_config_file(self, config_file: str | Path) -> None:
        """Save parameters to FIO config file.

        Args:
            config_file: Path to save FIO config file

        Raises:
            FIOConfigError: If parameters are not set or file cannot be written

        Example:
            ```python
            fio.save_config_file('test.fio')
            ```
        """
        if not self.parameters:
            raise FIOConfigError('No parameters to save')

        config = configparser.ConfigParser()
        config[self.parameters.name] = self.parameters.to_dict()

        try:
            with Path(config_file).open('w') as f:
                config.write(f)
        except OSError as e:
            raise FIOConfigError(f'Failed to write config file: {e}') from e

    def update_parameters(self, params: dict[str, Any]) -> None:
        """Update parameters.

        Args:
            params: Parameters to update

        Example:
            ```python
            fio.update_parameters({'runtime': 600, 'size': '20%'})
            ```
        """
        if not self.parameters:
            self.parameters = DefaultParameters(name='sts-fio-default')
        for key, value in params.items():
            setattr(self.parameters, key, value)

    def update_options(self, options: list[str]) -> None:
        """Update options.

        Args:
            options: Options to add

        Example:
            ```python
            fio.update_options(['minimal', 'readonly'])
            ```
        """
        self.options = list(set(self.options + options))

    def load_default_params(self) -> None:
        """Load default parameters.

        Example:
            ```python
            fio.load_default_params()
            ```
        """
        self.parameters = DefaultParameters(name='sts-fio-default')

    def load_fs_params(self) -> None:
        """Load filesystem parameters.

        Example:
            ```python
            fio.load_fs_params()
            ```
        """
        self.parameters = FileSystemParameters(name='sts-fio-fs')

    def load_block_params(self) -> None:
        """Load block device parameters.

        Example:
            ```python
            fio.load_block_params()
            ```
        """
        self.parameters = BlockDeviceParameters(name='sts-fio-block')

    def load_stress_params(self) -> None:
        """Load stress test parameters.

        Example:
            ```python
            fio.load_stress_params()
            ```
        """
        self.parameters = StressParameters(name='sts-fio-stress')

    def _create_command(self) -> str:
        """Create FIO command.

        Returns:
            FIO command string

        Raises:
            FIOConfigError: If parameters are not set or filename is missing
        """
        if not self.parameters:
            raise FIOConfigError('No parameters set')

        # Build command
        if self.config_file:
            command = f'fio {self.config_file}'
        else:
            if not self.filename:
                raise FIOConfigError('No filename set')
            params = ' '.join(f'--{k}="{v}"' for k, v in self.parameters.to_dict().items() if v)
            command = f'fio --filename "{self.filename}" {params}'

        # Add options
        if self.options:
            opts = ' '.join(f'--{opt}' for opt in self.options)
            command = f'{command} {opts}'

        return command

    def run(self) -> bool:
        """Run FIO test.

        Returns:
            True if successful, False otherwise

        Raises:
            FIOExecutionError: If FIO execution fails

        Example:
            ```python
            fio.run()
            True
            ```
        """
        try:
            command = self._create_command()
        except FIOConfigError as e:
            raise FIOExecutionError(f'Failed to create command: {e}') from e

        result = run(command)
        if not result.succeeded:
            logging.error(f'FIO run failed:\n{result.stderr}')
            return False

        logging.info('FIO executed successfully')
        return True
