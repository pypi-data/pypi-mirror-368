# Containerfile for STS CI environment
#
# This file defines a container image for CI pipelines to test sts-libs.

# Start from the official Fedora image
FROM fedora:latest

# Install all CI dependencies
# - hatch: For managing environments and running tests (pulls hatchling as dependency)
# - git: Required for version determination and pre-commit
# - pre-commit: For running pre-commit hooks
# - rubygems: Required for mkdocs pre-commit hook
# - packit: For packaging
RUN dnf -y makecache && \
    dnf install -y \
    hatch \
    git \
    pre-commit \
    rubygems \
    packit \
    && dnf clean all

# Set the working directory for CI operations
WORKDIR /sts

# Set environment variables for CI
ENV CI=true
ENV PYTHONUNBUFFERED=1
