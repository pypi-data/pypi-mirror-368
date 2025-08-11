# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

#!/bin/bash

set -euo pipefail
set -x

# Detect RHEL version
if [ -f /etc/os-release ]; then
    rhel_version=$(grep '^VERSION_ID=' /etc/os-release | cut -d'=' -f2 | tr -d '"')
else
    echo "Cannot detect RHEL version!" >&2
    exit 1
fi

rhel_major=$(echo "$rhel_version" | cut -d. -f1)
rhel_minor=$(echo "$rhel_version" | cut -d. -f2)

# RHEL version support check and Python binary selection
unsupported_msg="No support for this version. Exiting test."
if [[ "$rhel_major" -lt 8 ]]; then
    echo "RHEL major version is less than 8. $unsupported_msg"
    exit 0
elif [[ "$rhel_major" == "8" ]]; then
    if [[ -z "$rhel_minor" || "$rhel_minor" -lt 8 ]]; then
        echo "RHEL 8 minor version is less than 8. $unsupported_msg"
        exit 0
    fi
    pybin="python3.11"
else
    pybin="python3"
fi

# Install and configure pipx
$pybin -m pip install --user pipx
$pybin -m pipx ensurepath --force

# Clean up previous pytest venv
$pybin -m pipx uninstall pytest || true
rm -rf ~/.local/share/pipx/venvs/pytest

# Install pytest and inject dependencies
$pybin -m pipx install pytest --force
$pybin -m pipx inject pytest sts-libs pytest-variables[yaml] --force

# Remove removed drivers, or else upgrade cannot proceed
if lsmod | grep -q '^qla4xxx'; then
    echo "Removing qla4xxx kernel module for RHEL-10..."
    sudo modprobe -r qla4xxx
fi
