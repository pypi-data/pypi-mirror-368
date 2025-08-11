# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures related to kernel module management."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from sts.utils.modules import ModuleInfo, ModuleManager

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def managed_module(request: pytest.FixtureRequest) -> Generator[ModuleInfo, None, None]:
    """Fixture to manage the lifecycle (load/unload) of a kernel module for a test.

    Ensures the specified kernel module is loaded before the test runs and
    attempts to unload it after the test finishes.

    Configuration:
    - module_name: Name of the kernel module.
      Set via parametrize: @pytest.mark.parametrize('managed_module', ['qedi'], indirect=True)
    """
    module_name = getattr(request, 'param', None)
    if not module_name:
        pytest.skip('Module name not provided to managed_module fixture')

    logging.info(f'Setting up managed module: {module_name}')
    mm = ModuleManager()
    module_info = ModuleInfo(name=module_name)

    # Store initial state
    was_initially_loaded = module_info.loaded

    # Setup: Load the module
    if not module_info.loaded:
        logging.info(f'Module {module_name} not loaded, attempting load.')
        if not mm.load(module_name):
            pytest.skip(f'Failed to load required module {module_name}')
        # Re-check info after load attempt
        module_info = ModuleInfo(name=module_name)
        if not module_info.loaded:
            pytest.skip(f'Module {module_name} still not loaded after load attempt')
        logging.info(f'Module {module_name} loaded successfully.')
    else:
        logging.info(f'Module {module_name} was already loaded.')

    yield module_info

    # Teardown: Only unload if it wasn't loaded initially
    if not was_initially_loaded:
        logging.info(f'Unloading module {module_name} to restore initial state')
        try:
            # Re-fetch info in case state changed during test
            module_info_teardown = ModuleInfo(name=module_name)
            if module_info_teardown.loaded:
                if not mm.unload(module_name):
                    logging.warning(f'Failed to unload module {module_name} during fixture teardown.')
                else:
                    logging.info(f'Successfully unloaded module {module_name} during fixture teardown.')
        except Exception:
            logging.exception(f'Error unloading module {module_name} during fixture teardown.')
    else:
        logging.info(f'Keeping module {module_name} loaded as it was initially loaded')

    logging.info(f'Finished teardown for managed_module: {module_name}')
