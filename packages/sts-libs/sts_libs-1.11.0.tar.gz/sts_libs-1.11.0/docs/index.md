# sts - Storage Tests

Project designed for testing Linux storage drivers, utilities, and devices
on Fedora, CentOS Stream, and RHEL. It consists of two main parts:

1. **sts-libs**: A Python package published to PyPA and Fedora Copr
   - Requires Python 3.9+, pytest, and pytest-testinfra
   - Makes writing storage tests quick and easy
   - Supports RHEL8, RHEL9, RHEL10, CentOS Stream 9 and 10
   - Available via pip and Fedora Copr (including EPEL)

1. **Tests, Plans**: A collection of tests and plans for testing storage devices
   - Uses pytest and [tmt](https://tmt.readthedocs.io/en/stable/)
   - Made to be executed with tmt (and testing-farm)
   - Utilizes sts-libs for test implementation

## Quick Start

### Installing sts-libs

#### From PyPI

```bash
pip install sts-libs
```

#### From Fedora Copr (Fedora and EPEL)

```bash
dnf copr enable packit/gitlab.com-rh-kernel-stqe-sts-releases
dnf install python3-sts-libs
```

### Running Tests

Tests are executed using tmt.
For common usage, see:

```bash
tldr tmt
```

Full documentation for tmt is available at [tmt.readthedocs.io](https://tmt.readthedocs.io/en/stable/).
tmt Matrix room is available at [#tmt:fedora.im](https://matrix.to/#/#tmt:fedora.im).

## Project Structure

```bash
.
├── sts_libs/
│   ├── src/sts/       # libs, fixtures
│   └── tests/         # sts-libs unit tests
├── plans/
└── tests/
```

## Requirements

### sts-libs

- Python 3.9+
- pytest
- pytest-testinfra

### Supported Operating Systems

- Fedora
- CentOS Stream 9 and 10
- RHEL 8, 9, and 10

Other operating systems may work but would need community contributions for support.
