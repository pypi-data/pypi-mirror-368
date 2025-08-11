# sts-libs Development Container

This directory contains files for creating and running container environments
for sts-libs development, unit testing, and CI.

## What is this for?

These containers are specifically designed for developing and testing the sts-libs package itself,
not for developing tests that use sts-libs. They provide:

- A consistent environment for running sts-libs unit tests
- Fast validation of your changes to the library
- A clean Fedora-based environment regardless of your host OS
- A ready-to-use CI container for GitLab pipelines

## Container Types

This directory provides two main container types:

1. **Development Container** (`sts-dev`): For local development and testing
2. **CI Container** (`sts-ci`): For continuous integration pipelines

Both use a common base image with pre-cached DNF metadata for faster builds.

## When to use these containers

- ✅ When developing or improving the sts-libs library itself
- ✅ When running unit tests for the sts-libs library
- ✅ When you need to debug issues with the library in isolation
- ✅ When setting up CI pipelines for sts-libs testing

## When NOT to use these containers

- ❌ For developing actual storage tests that use sts-libs
- ❌ For running the full test suite of storage tests

## Setup

### Prerequisites

- Podman installed on your system
- Basic familiarity with container concepts

### Building the containers

- For local development only:

```bash
cd dev-container
./build.sh
```

- To build both development and CI containers:

```bash
cd dev-container
./build.sh --with-ci
```

The script will:

1. Create a base Fedora image with pre-cached DNF metadata (for faster builds)
2. Build the development container
3. (Optionally) Build the CI container

## Using the Development Container

After building, you can use the included `run.sh` script:

```bash
# Run all sts-libs unit tests
./run.sh test

# Run specific unit tests
./run.sh test -k test_blockdevice

# Get an interactive shell
./run.sh shell

# Run a custom command
./run.sh run uv --version
```

## Using the CI Container

The CI container can be pushed to a registry like Quay.io and used in GitLab CI:

```yaml
# .gitlab-ci.yml example
test-libs:
  image: quay.io/your-org/sts-ci:latest
  script:
    - pre-commit run --all-files --show-diff-on-failure
    - hatch run check  # pyright
    - hatch run test   # pytest with coverage
```

## How it works

- The containers mount your local STS directory as a volume,
  so any changes you make to the code are immediately available in the container.
- Tests run with the `--with-editable` flag, which uses your local code (not a PyPI package).
- The containers are stateless - changes made inside are lost when they exit (except for changes to mounted files).

## For developing storage tests

If you want to develop or run tests that use sts-libs, you should use TMT instead:

```bash
# Start a container for test development (from a test directory)
tmt try fedora@container

# Use the sts-dev container interactively for troubleshooting
tmt try sts-dev@container --login
```

For more information about TMT, you can use:

```bash
# Quick reference guide
tldr tmt

# Detailed help
tmt --help
```
