# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Utility modules for storage testing.

This package provides various utility modules for storage testing:

System Utilities:
- system.py: System information and management
- packages.py: Package management operations
- processes.py: Process management and control
- modules.py: Kernel module operations
- files.py: File operations and management

Command Line:
- cmdline.py: Command execution and output handling
- log.py: Logging utilities
- syscheck.py: System checks and validation

Size and Conversion:
- size.py: Size conversion and formatting utilities

Testing Support:
- tmt.py: Test Management Tool integration
- errors.py: Common error types

Example:
    ```python
    from sts.utils import system

    sys_mgr = system.SystemManager()
    sys_mgr.get_logs()

    from sts.utils import size

    size.size_human_2_size_bytes('1KiB')
    1024
    ```
"""
