# sts-libs Documentation

This section contains the API documentation for the sts-libs package,
automatically generated from the source code docstrings.

## Overview

sts-libs is a Python library designed for storage testing, providing a comprehensive set of
tools and abstractions for working with various storage technologies on Linux systems.

## Components

The library is organized into three main components:

### Test Fixtures

Pytest fixtures that handle test setup and teardown, making it easy to create reproducible storage test environments.
These fixtures handle common tasks like device creation, configuration, and cleanup.

See the [Test Fixtures](fixtures.md) page for details.

### Storage Libraries

Core functionality for interacting with different storage subsystems. Each library provides a high-level interface
to its respective storage technology, abstracting away the complexity of direct system interaction.

### Utilities

Common helper functions and classes that support the main libraries. These utilities handle tasks
like command execution, system management, and data conversion.

Check the [Utilities](utils.md) page for available tools.

## Usage

Each module's documentation includes usage examples and best practices for working with the library.

## Navigation

- Use the navigation menu to browse different sections
- Each storage library has its own dedicated page with complete documentation
- Code examples show how to use the APIs effectively
