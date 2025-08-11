# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Package management.

This module provides functionality for managing system packages:
- Package installation
- Package information
- Package version management
- Repository management
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from sts import get_sts_host
from sts.utils.cmdline import run

if TYPE_CHECKING:
    from testinfra.modules.base import RpmPackage  # type: ignore[no-redef]

host = get_sts_host()


@dataclass
class RepoConfig:
    """Repository configuration.

    This class provides configuration for repository management:
    - Repository metadata
    - Repository options
    - Repository URLs

    Args:
        name: Repository name
        baseurl: Repository URL (optional)
        metalink: Repository metalink (optional)
        enabled: Enable repository
        gpgcheck: Enable GPG check
        skip_if_unavailable: Skip if unavailable

    Example:
        ```python
        config = RepoConfig(
            name='epel',
            baseurl='https://dl.fedoraproject.org/pub/epel/8/Everything/x86_64/',
        )
        ```
    """

    name: str
    baseurl: str | None = None
    metalink: str | None = None
    enabled: bool = True
    gpgcheck: bool = False
    skip_if_unavailable: bool = True

    def to_config(self) -> dict[str, str]:
        """Convert to repository configuration.

        Returns:
            Repository configuration dictionary

        Example:
            ```python
            config = RepoConfig(name='epel', baseurl='https://example.com')
            config.to_config()
            {'name': 'epel', 'baseurl': 'https://example.com', 'enabled': '1', ...}
            ```
        """
        config = {
            'name': self.name,
            'enabled': '1' if self.enabled else '0',
            'gpgcheck': '1' if self.gpgcheck else '0',
            'skip_if_unavailable': '1' if self.skip_if_unavailable else '0',
        }
        if self.baseurl:
            config['baseurl'] = self.baseurl
        if self.metalink:
            config['metalink'] = self.metalink
        return config


class Dnf:
    """DNF package manager functionality.

    This class provides functionality for managing system packages:
    - Package installation
    - Package removal
    - Repository management

    Example:
        ```python
        pm = Dnf()
        pm.install('bash')
        True
        ```
    """

    def __init__(self) -> None:
        """Initialize package manager."""
        self.repo_path = Path('/etc/yum.repos.d')

    def install(self, package: str) -> bool:
        """Install package.

        Args:
            package: Package name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pm.install('bash')
            True
            ```
        """
        pkg: RpmPackage = host.package(package)  # type: ignore[no-any-return]
        if pkg.is_installed:
            return True

        result = run(f'dnf install -y {package}')
        if result.failed:
            logging.error(f'Failed to install {package}:\n{result.stderr}')
            return False

        logging.info(f'Successfully installed {package}')
        return True

    def remove(self, package: str) -> bool:
        """Remove package.

        Args:
            package: Package name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pm.remove('bash')
            True
            ```
        """
        pkg: RpmPackage = host.package(package)  # type: ignore[no-any-return]
        if not pkg.is_installed:
            return True

        result = run(f'dnf remove -y {package}')
        if result.failed:
            logging.error(f'Failed to remove {package}:\n{result.stderr}')
            return False

        logging.info(f'Successfully removed {package}')
        return True

    def add_repo(self, config: RepoConfig) -> bool:
        """Add repository.

        Args:
            config: Repository configuration

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            config = RepoConfig(
                name='epel',
                baseurl='https://dl.fedoraproject.org/pub/epel/8/Everything/x86_64/',
            )
            pm.add_repo(config)
            True
            ```
        """
        if not config.baseurl and not config.metalink:
            logging.error('Either baseurl or metalink required')
            return False

        repo_file = self.repo_path / f'{config.name.lower()}.repo'
        if repo_file.exists():
            logging.info(f'Repository {config.name} already exists')
            return True

        # Write repo file
        try:
            content = [f'[{config.name}]']
            content.extend(f'{k}={v}' for k, v in config.to_config().items())
            repo_file.write_text('\n'.join(content))
        except OSError:
            logging.exception(f'Failed to write repository file {repo_file}')
            return False

        return True

    def remove_repo(self, name: str) -> bool:
        """Remove repository.

        Args:
            name: Repository name

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pm.remove_repo('epel')
            True
            ```
        """
        repo_file = self.repo_path / f'{name.lower()}.repo'
        try:
            repo_file.unlink(missing_ok=True)
        except OSError:
            logging.exception(f'Failed to remove repository file {repo_file}')
            return False

        return True

    def repo_exists(self, name: str) -> bool:
        """Check if repository exists.

        Args:
            name: Repository name

        Returns:
            True if repository exists

        Example:
            ```python
            pm.repo_exists('epel')
            True
            ```
        """
        result = run(f'dnf repoinfo {name}')
        if result.failed:
            logging.error(f'Repository {name} not found:\n{result.stderr}')
            return False
        return True

    def repo_enabled(self, name: str) -> bool:
        """Check if repository is enabled.

        Args:
            name: Repository name

        Returns:
            True if repository exists and is enabled

        Example:
            ```python
            pm.repo_enabled('epel')
            True
            ```
        """
        if not self.repo_exists(name):
            return False

        result = run(f'dnf repoinfo {name}')
        if 'enabled' not in result.stdout:
            logging.error(f'Repository {name} not enabled:\n{result.stderr}')
            return False

        return True

    def download_repo(self, url: str, name: str | None = None, *, overwrite: bool = True) -> bool:
        """Download repository file.

        Args:
            url: Repository file URL
            name: Repository name (optional, derived from URL)
            overwrite: Overwrite existing file (optional)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pm.download_repo('https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm')
            True
            ```
        """
        if not self.install('curl'):
            return False

        if not name:
            name = url.split('/')[-1]
        if not name.endswith('.repo'):
            name = f'{name}.repo'

        repo_file = self.repo_path / name
        if repo_file.exists() and not overwrite:
            logging.info(f'Repository file {repo_file} already exists')
            return True

        result = run(f'curl {url} --output {repo_file}')
        if result.failed:
            logging.error(f'Failed to download repository file from {url}:\n{result.stderr}')
            return False

        return True


class RpmOstree:
    """RPM-OSTree package manager functionality.

    This class provides functionality for managing system packages using RPM-OSTree:
    - Package installation
    - Package removal

    """

    def install(self, package: str) -> bool:
        """Install package.

        Args:
            package: Package name

        Returns:
            True if successful, False otherwise

        """
        pkg: RpmPackage = host.package(package)  # type: ignore[no-any-return]
        if pkg.is_installed:
            return True

        result = run(f'rpm-ostree install --apply-live --idempotent --allow-inactive --assumeyes {package}')
        if result.failed:
            logging.error(f'Failed to install {package}:\n{result.stderr}')
            return False

        logging.info(f'Successfully installed {package}')
        return True

    def remove(self, package: str) -> bool:
        """Remove package.

        Args:
            package: Package name

        Returns:
            True if successful, False otherwise

        """
        pkg: RpmPackage = host.package(package)  # type: ignore[no-any-return]
        if not pkg.is_installed:
            return True

        result = run(f'rpm-ostree uninstall --assumeyes {package}')
        if result.failed:
            logging.error(f'Failed to remove {package}:\n{result.stderr}')
            return False

        logging.info(f'Successfully removed {package}')
        return True


def check_rpm_ostree_status() -> bool:
    """Check the status of rpm-ostree.

    Returns:
        True if rpm-ostree status returns 0, False otherwise
    """
    return run('rpm-ostree status').succeeded


def ensure_installed(*packages: str) -> bool:
    """Ensure packages are installed.

    Args:
        *packages: Package names to install

    Returns:
        True if all packages are installed, False otherwise

    Example:
        ```python
        ensure_installed('lsscsi', 'curl')
        True
        ensure_installed('nonexistent')
        False
        ```
    """
    pm = RpmOstree() if check_rpm_ostree_status() else Dnf()

    for package in packages:
        if not host.package(package).is_installed:  # type: ignore[no-any-return]
            return all(pm.install(package) for package in packages)
    return True


def log_package_versions(*package_names: str) -> None:
    """Log package version(s) using host object.

    Args:
        *package_names: Package name(s) to log versions for

    Example:
        ```python
        # Single package
        log_package_versions('bash')
        # Logs: Package bash version: 5.1.8-1.el9

        # Multiple packages
        log_package_versions('bash', 'curl', 'vim')
        # Logs: Package bash version: 5.1.8-1.el9
        #       Package curl version: 7.76.1-19.el9
        #       Package vim version: not installed
        ```
    """
    for package_name in package_names:
        pkg: RpmPackage = host.package(package_name)  # type: ignore[no-any-return]
        if not pkg.is_installed:
            logging.info(f'Package {package_name} version: not installed')
        else:
            version = f'{pkg.version}-{pkg.release}'
            logging.info(f'Package {package_name} version: {version}')
