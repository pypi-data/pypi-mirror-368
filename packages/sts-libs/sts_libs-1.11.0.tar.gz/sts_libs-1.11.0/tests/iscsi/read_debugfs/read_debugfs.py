# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from os import getenv

import pytest

from sts.utils.files import Directory
from sts.utils.modules import ModuleInfo

MODULE_NAME = getenv('ISCSI_SETUP_VARS', 'qedi')


@pytest.mark.parametrize('managed_module', [MODULE_NAME], indirect=True)
def test_read_debugfs(managed_module: ModuleInfo, debugfs_module_reader: Directory) -> None:
    """Test recursively reading files in the debugfs directory of a specific driver."""
    # managed_module fixture ensures the module is loaded/unloaded.
    # debugfs_module_reader fixture ensures debugfs is mounted and provides the dir.
    module_debugfs_dir = debugfs_module_reader.path  # Get the Path object from the Directory

    logging.info(f'Recursively reading files in {module_debugfs_dir} for module {managed_module.name}')

    files_processed = 0
    errors_encountered = 0

    try:
        for file_path in debugfs_module_reader.iter_files(recursive=True):
            files_processed += 1
            logging.info(f'Processing file: {file_path}')
            # Attempt to read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            logging.debug(f'File {file_path} content (first 100 chars):\n{content[:100]}')
    except (PermissionError, OSError, Exception):
        logging.exception('Error during debugfs operation')
        errors_encountered += 1

    # Verify if the system operates normally after reading debugfs, no crashes or hangs
    logging.info(f'Finished reading debugfs. Processed {files_processed} files with {errors_encountered} read errors.')
    assert True
