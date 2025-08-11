# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Script to sync STS repository to a remote host using rsync.

Could be useful in some scenarios during sts-libs development.
For test development, use tmt try.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from enum import Enum, auto
from pathlib import Path


def get_exclude_patterns() -> list[str]:
    """Get rsync exclude patterns.

    Returns:
        List of patterns to exclude
    """
    return [
        # Virtual environments
        'venv/',
        '.venv/',
        '/opt/venv/',
        # Python cache
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache/',
        # Hidden files and directories
        '/.*cache',
        # Build artifacts
        '*.egg-info/',
        'build/',
        'dist/',
    ]


def get_pyproject_hash(repo_path: Path) -> str:
    """Get hash of pyproject.toml contents.

    Args:
        repo_path: Path to repository root

    Returns:
        SHA256 hash of pyproject.toml contents
    """
    pyproject = repo_path / 'pyproject.toml'
    if not pyproject.exists():
        return ''
    return hashlib.sha256(pyproject.read_bytes()).hexdigest()


def check_venv_exists(host: str) -> bool:
    """Check if virtual environment exists on remote host.

    Args:
        host: Remote host in format root@ip

    Returns:
        True if venv exists and is valid, False otherwise
    """
    venv_path = '/opt/venv/sts'
    try:
        # Check if venv exists and has pip
        result = subprocess.run(
            ['ssh', host, f'test -f {venv_path}/bin/pip'],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0  # noqa: TRY300
    except Exception:  # noqa: BLE001
        return False


def check_venv_needs_update(host: str, repo_path: Path) -> bool:
    """Check if virtual environment needs to be updated.

    Args:
        host: Remote host in format root@ip
        repo_path: Path to repository root

    Returns:
        True if venv needs update, False otherwise
    """
    # Always update if venv doesn't exist
    if not check_venv_exists(host):
        return True

    # Get local pyproject hash
    local_hash = get_pyproject_hash(repo_path)
    if not local_hash:
        return True  # No pyproject.toml, force update

    # Get remote hash
    try:
        result = subprocess.run(
            ['ssh', host, 'sha256sum /root/sts/pyproject.toml'],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_hash = result.stdout.split()[0]
    except subprocess.CalledProcessError:
        return True  # Error getting remote hash, force update
    return local_hash != remote_hash


class VenvAction(Enum):
    """Virtual environment action."""

    UPDATE = auto()  # Update existing venv
    CREATE = auto()  # Create new venv
    VERIFY = auto()  # Just verify venv exists


def setup_venv(host: str, action: VenvAction) -> int:
    """Set up Python virtual environment on remote host.

    Args:
        host: Remote host in format root@ip
        action: Action to perform on venv

    Returns:
        Exit code from ssh command
    """
    venv_path = '/opt/venv/sts'
    commands = []

    if action in (VenvAction.UPDATE, VenvAction.CREATE):
        commands.extend(
            [
                f'rm -rf {venv_path}',  # Remove old/invalid venv
                f'mkdir -p {venv_path}',
                f'python3 -m venv {venv_path}',
                f'{venv_path}/bin/pip install --upgrade pip',
                f'cd /root/sts && {venv_path}/bin/pip install -e .',
            ]
        )

        # Add alias only on first install
        if action == VenvAction.CREATE:
            alias_cmd = f"alias sts='source {venv_path}/bin/activate'"
            commands.extend(
                [
                    f'grep -q "{alias_cmd}" ~/.bashrc || echo "{alias_cmd}" >> ~/.bashrc',
                    'source ~/.bashrc',  # Reload bashrc
                ]
            )
    else:
        # Just ensure venv directory exists
        commands.append(f'mkdir -p {venv_path}')

    try:
        # Run commands over SSH
        cmd = ['ssh', host, ' && '.join(commands)]
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return e.returncode
    except Exception:  # noqa: BLE001
        return 1
    else:
        return result.returncode


def sync_repo(host: str, repo_path: Path | None = None) -> int:
    """Sync repository to remote host using rsync.

    Args:
        host: Remote host in format root@ip
        repo_path: Path to repository root (default: current directory)

    Returns:
        Exit code from rsync command
    """
    repo_path = repo_path or Path.cwd()

    # Ensure we're in the repo root
    if not (repo_path / '.git').exists():
        return 1

    # Build rsync command
    cmd = ['rsync', '-avz', '--delete']

    # Add exclude patterns
    for pattern in get_exclude_patterns():
        cmd.extend(['--exclude', pattern])

    # Add source and destination
    source = str(repo_path) + '/'  # Trailing slash to sync contents
    destination = f'{host}:/root/sts/'
    cmd.extend([source, destination])

    try:
        # Run rsync
        result = subprocess.run(cmd, check=True)
        if result.returncode != 0:
            return result.returncode

        # Check if venv needs update
        needs_update = check_venv_needs_update(host, repo_path)
        is_new_install = not check_venv_exists(host)

        # Set up virtual environment
        action = VenvAction.CREATE if is_new_install else VenvAction.UPDATE if needs_update else VenvAction.VERIFY
        return setup_venv(host, action)

    except subprocess.CalledProcessError as e:
        return e.returncode
    except Exception:  # noqa: BLE001
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Sync STS repository to remote host')
    parser.add_argument('host', help='Remote host in format root@ip')
    args = parser.parse_args()

    return sync_repo(args.host)


if __name__ == '__main__':
    sys.exit(main())
