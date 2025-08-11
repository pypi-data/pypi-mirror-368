# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSNS Client Configuration and Management Module.

This module provides classes and functions to manage the configuration and operations of the
iSNS (Internet Storage Name Service) client. It includes a configuration class for handling iSNS client settings
and a wrapper class for interacting with the `isnsadm` command-line tool.

"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sts.utils.cmdline import run
from sts.utils.config import Config
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from testinfra.backend.base import CommandResult


class IsnsadmConf(Config):
    """iSNS client configuration file.

    The configuration options include:
        - ServerAddress: The address of the iSNS server.
        - Authentication: Authentication settings for the client.
        - private key, public key
        - Security: Security settings for the client.
        - Network: Network-related settings for the client.
    """

    CONFIG_PATH = Path('/etc/isns/isnsadm.conf')

    def __init__(self) -> None:
        """Initialize the IsnsadmConf instance."""
        super().__init__(self.CONFIG_PATH)


class IsnsAdm:
    """Wrapper for isnsadm command line tool and configuration management.

    Manages isnsadm operations:
        - Register/Deregister objects
        - List objects
    """

    CLI_NAME = 'isnsadm'
    PACKAGE_NAME = 'isns-utils'
    SERVICE_NAME = 'isnsd'

    def __init__(self, debug: str | None = None) -> None:
        """Initialize the IsnsAdm instance.

        Args:
            config_path: Path to the configuration file
            debug: Debug flags
                socket: Network send/receive
                auth: Authentication and security related information
                message: iSNS protocol layer
                state: Database state
                scn: SCN (state change notification) messages
                esi: ESI (entity status inquiry) messages
                all: All of the above
        """
        self.debug = debug

        # Ensure package is installed
        system = SystemManager()
        if not system.package_manager.install(self.PACKAGE_NAME):
            logging.critical(f'Could not install {self.PACKAGE_NAME}')

        # Start isnsd service
        if not system.service_start(self.SERVICE_NAME):
            logging.critical(f'Could not start {self.SERVICE_NAME} service')

    def _run(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Run the isnsadm command."""
        command = [self.CLI_NAME]
        if self.debug:
            command.extend(['--debug', self.debug])
        if args:
            command.extend(args)  # type: ignore [arg-type]
        if kwargs:
            for key, value in kwargs.items():
                if value is not None:
                    command.extend([f'{key},{value}'])

        return run(' '.join(command))

    def register(self, **kwargs: str | None) -> CommandResult:
        """Register objects with isnsadm."""
        return self._run('--register', **kwargs)

    def list_objects(self, *args: str | None) -> CommandResult:
        """List objects with isnsadm.

        Possible type names are: entities, nodes, portals, dds, ddsets, portal-groups, and policies.
        https://www.mankier.com/8/isnsadm
        """
        return self._run('--list', *args)
