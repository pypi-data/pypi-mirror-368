# sts-libs

[![PyPI version](https://badge.fury.io/py/sts-libs.svg)](https://badge.fury.io/py/sts-libs)
[![Downloads](https://pepy.tech/badge/sts-libs)](https://pepy.tech/project/sts-libs)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://rh-kernel-stqe.gitlab.io/sts)
[![Copr build status](https://img.shields.io/badge/dynamic/json?color=blue&label=copr&query=builds.latest.state&url=https%3A%2F%2Fcopr.fedorainfracloud.org%2Fapi_3%2Fpackage%3Fownername%3Dpackit%26projectname%3Dgitlab.com-rh-kernel-stqe-sts-releases%26packagename%3Dpython-sts-libs%26with_latest_build%3DTrue)](https://copr.fedorainfracloud.org/coprs/packit/gitlab.com-rh-kernel-stqe-sts-releases/)

Python library for storage testing on Fedora-based Linux distributions.

## About

sts-libs provides a comprehensive set of tools and utilities for storage testing, designed to work seamlessly
with [pytest](https://pytest.org) and the [testinfra](https://testinfra.readthedocs.io) pytest plugin.
It is a core component of the [sts](https://gitlab.com/rh-kernel-stqe/sts) testing framework, which
uses [tmt](https://github.com/teemtee/tmt) for test management.

Full documentation is available at [rh-kernel-stqe.gitlab.io/sts](https://rh-kernel-stqe.gitlab.io/sts)

## Status

Approaching 1.0 release with a stable-ish API and extensible architecture. Currently supports core storage technologies,
with a design that makes it straightforward to add support for additional devices and protocols.

## Installation

### Fedora and EPEL9

RPM packages are available on [Fedora Copr](https://copr.fedorainfracloud.org/coprs/packit/gitlab.com-rh-kernel-stqe-sts-releases/)

### Pytest virtual environment with uv

```bash
uv tool install pytest --with sts-libs
```

### Libs only with pip

```bash
pip install sts-libs
```

## Contributing

We welcome contributions! Please see our [contributing guide](https://rh-kernel-stqe.gitlab.io/sts/contributing/)
for details on how to get involved.

Issues and merge requests can be submitted at the [sts GitLab repository](https://gitlab.com/rh-kernel-stqe/sts).
