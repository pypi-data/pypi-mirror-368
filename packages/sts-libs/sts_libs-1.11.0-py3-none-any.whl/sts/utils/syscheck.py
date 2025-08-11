# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""System state checker.

This module provides functionality to check system state:
- Kernel state (tainted, dumps)
- System logs (dmesg, messages)
- Crash dumps (kdump, abrt)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from os import getenv
from pathlib import Path

from sts import get_sts_host
from sts.utils.cmdline import run
from sts.utils.system import SystemManager

# Error patterns to check for
SEGFAULT_MSG = 'segfault'
CALLTRACE_MSG = 'Call Trace:'
ERROR_MSGS = [SEGFAULT_MSG, CALLTRACE_MSG]

# Test data directory
TMT_TEST_DATA = getenv('TMT_TEST_DATA', '.')
LOG_PATH = Path(TMT_TEST_DATA)

# System manager instance
system = SystemManager()
host = get_sts_host()


def check_all() -> bool:
    """Check for errors on the system.

    Returns:
        True if no errors found, False otherwise

    Example:
        ```python
        check_all()
        True
        ```
    """
    logging.info('Checking for errors on the system')
    error_count = 0

    # Run all checks
    checks = [
        kernel_check,
        abrt_check,
        messages_dump_check,
        dmesg_check,
        kdump_check,
    ]

    for check in checks:
        if not check():
            error_count += 1

    if error_count:
        # Save system logs
        messages = Path('/var/log/messages')
        if messages.is_file():
            logging.info('Saving /var/log/messages')
            target = LOG_PATH / 'messages.log'
            target.write_bytes(messages.read_bytes())

        # Generate sosreport if available
        # testinfra host.package.is_installed does indeed work, but type checkers doesn't like it too much
        if host.package('sos').is_installed and (sos_file := system.generate_sosreport()):  # pyright: ignore[reportUnknownMemberType, reportCallIssue, reportAttributeAccessIssue]
            logging.info(f'Generated sosreport: {sos_file}')

        return False

    return True


def abrt_check() -> bool:
    """Check if abrtd found any issues.

    Returns:
        True if no errors found, False otherwise

    Example:
        ```python
        abrt_check()
        True
        ```
    """
    logging.info('Checking abrt for errors')

    # Check if abrt is installed
    result = run('rpm -q abrt')
    if result.failed:
        logging.warning('abrt not installed, skipping check')
        return True

    # Check if abrtd is running
    result = run('pidof abrtd')
    if result.failed:
        logging.error('abrtd not running')
        return False

    # Check for issues
    result = run('abrt-cli list')
    if result.failed:
        logging.error('abrt-cli failed')
        return False

    # Parse output for directories
    error = False
    for line in result.stdout.splitlines():
        if match := re.match(r'Directory:\s+(\S+)', line):
            directory = match.group(1)
            filename = f'{directory.replace(":", "-")}.tar.gz'
            logging.info(f'Found abrt issue: {filename}')

            # Archive directory
            run(f'tar cfzP {filename} {directory}')
            target = LOG_PATH / filename
            Path(filename).rename(target)

            # Remove from abrt to avoid affecting next test
            run(f'abrt-cli rm {directory}')
            error = True

    if error:
        logging.error('Found abrt errors')
        return False

    logging.info('No abrt errors found')
    return True


def kernel_check() -> bool:
    """Check if kernel is tainted.

    Returns:
        True if kernel is not tainted, False otherwise

    Example:
        ```python
        kernel_check()
        True
        ```
    """
    logging.info('Checking for tainted kernel')

    # Get current tainted value
    result = run('cat /proc/sys/kernel/tainted')
    if result.failed:
        logging.error('Failed to get tainted value')
        return False

    tainted = int(result.stdout)
    if tainted == 0:
        return True

    logging.warning('Kernel is tainted!')

    # Check tainted bits
    bit = 0
    value = tainted
    while value:
        if value & 1:
            logging.info(f'TAINT bit {bit} is set')
        bit += 1
        value >>= 1

    # List tainted module definitions
    result = run('cat /usr/src/kernels/`uname -r`/include/linux/kernel.h | grep TAINT_')
    if result.succeeded:
        logging.info('Tainted bit definitions:')
        logging.info(result.stdout)

    # Check for tainted modules
    result = run("cat /proc/modules | grep -e '(.*)' | cut -d' ' -f1")
    if result.failed:
        return False

    # Skip certain modules
    ignore_modules = {'ocrdma', 'nvme_fc', 'nvmet_fc', 'kvdo'}  # Tech Preview modules
    found_issue = False

    for module in result.stdout.splitlines():
        if not module:
            continue

        logging.info(f'Found tainted module: {module}')
        run(f'modinfo {module}')

        if module in ignore_modules:
            logging.info(f'Ignoring known tainted module: {module}')
            continue

        found_issue = True

    return not found_issue


def messages_dump_check() -> bool:
    """Check for kernel dumps in system messages.

    Returns:
        True if no dumps found, False otherwise

    Example:
        ```python
        messages_dump_check()
        True
        ```
    """
    logging.info('Checking for kernel dumps')

    messages = Path('/var/log/messages')
    if not messages.is_file():
        logging.warning('No messages file found')
        return True

    # Read messages file
    try:
        content = messages.read_text()
    except UnicodeDecodeError:
        content = messages.read_text(encoding='latin-1')

    # Search for dumps
    begin = r'\[ cut here \]'
    end = r'\[ end trace '
    pattern = f'{begin}(.*?){end}'

    if dumps := re.findall(pattern, content, re.MULTILINE):
        logging.error('Found kernel dumps:')
        for dump in dumps:
            logging.error(dump)
        return False

    logging.info('No kernel dumps found')
    return True


def dmesg_check() -> bool:
    """Check for errors in dmesg.

    Returns:
        True if no errors found, False otherwise

    Example:
        ```python
        dmesg_check()
        True
        ```
    """
    logging.info('Checking dmesg for errors')

    for msg in ERROR_MSGS:
        result = run(f"dmesg | grep -i '{msg}'")
        if result.succeeded:
            logging.error(f'Found error in dmesg: {msg}')
            target = LOG_PATH / 'dmesg.log'
            target.write_text(run('dmesg').stdout)
            return False

    run('dmesg -c')  # Clear dmesg
    logging.info('No errors found in dmesg')
    return True


def kdump_check() -> bool:
    """Check for kdump crash files.

    Returns:
        True if no crashes found, False otherwise

    Example:
        ```python
        kdump_check()
        True
        ```
    """
    logging.info('Checking for kdump crashes')

    # Get hostname
    result = run('hostname')
    if result.failed:
        logging.error('Failed to get hostname')
        return False

    hostname = result.stdout.strip()
    crash_dir = Path('/var/crash') / hostname

    if not crash_dir.exists():
        logging.info('No kdump directory found')
        return True

    # Get crash timestamps
    crashes = []
    for crash in crash_dir.iterdir():
        if match := re.match(r'.*?-(.*)', crash.name):
            date = match.group(1).replace('.', '-')
            index = date.rfind('-')
            date = f'{date[:index]} {date[index + 1 :]}'
            crashes.append(date)

    if not crashes:
        logging.info('No kdump crashes found')
        return True

    # Check crash times
    now = datetime.now(timezone.utc).timestamp()
    for crash in crashes:
        result = run(f'date --date="{crash}" +%s')
        if result.failed:
            logging.warning(f'Failed to parse crash date: {crash}')
            continue

        crash_time = int(result.stdout)
        if crash_time > now - 86400:  # Last 24 hours
            logging.error(f'Found recent crash: {crash}')
            return False

    logging.info('No recent kdump crashes found')
    return True
