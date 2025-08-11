#!/bin/bash
# Container runner script for STS-libs development
#
# This script provides a convenient interface for running the STS development
# container specifically for sts-libs library development and unit testing.
# It handles mounting the project directory and provides shortcuts
# for common operations.

# Determine the project root directory (parent of this script's directory)
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Container image name
IMAGE="sts-dev:latest"

# Help function to show usage
show_help() {
    echo "STS-libs Development Container Runner"
    echo
    echo "Usage: ./run.sh [COMMAND]"
    echo
    echo "Commands:"
    echo "  test              Run sts-libs unit tests"
    echo "  shell             Start a shell in the container"
    echo "  run [COMMAND]     Run a custom command in the container"
    echo "  help              Show this help message"
    echo
    echo "Examples:"
    echo "  ./run.sh test                      # Run all unit tests"
    echo "  ./run.sh test -k test_blockdevice  # Run specific unit tests"
    echo "  ./run.sh shell                     # Get a shell"
    echo "  ./run.sh run uv --version          # Run a custom command"
    echo
    echo "NOTE: This container is ONLY for sts-libs library development"
    echo "      For developing actual tests that use sts-libs, use:"
    echo "      tmt try fedora@container"
}

# Function to check if the image exists
check_image() {
    if ! podman image exists "$IMAGE"; then
        echo "Error: Container image $IMAGE not found."
        echo "Run './build.sh' in the dev-container directory first."
        exit 1
    fi
}

# Check if the image exists
check_image

# Handle the command
case "$1" in
    test)
        shift
        echo "Running sts-libs unit tests in container..."
        podman run --rm -v "$PROJECT_ROOT:/sts:Z" "$IMAGE" \
            uv tool run --with-editable /sts --with pytest-coverage pytest sts_libs/tests "$@"
        ;;
    shell)
        echo "Starting shell in container for sts-libs development..."
        podman run --rm -it -v "$PROJECT_ROOT:/sts:Z" "$IMAGE" bash
        ;;
    run)
        shift
        podman run --rm -v "$PROJECT_ROOT:/sts:Z" "$IMAGE" "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
