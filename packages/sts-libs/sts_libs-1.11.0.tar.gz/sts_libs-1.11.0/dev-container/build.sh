#!/bin/bash
# Script to build optimized containers for STS-libs development and CI
#
# This script builds container images for:
# 1. Developing and unit testing the sts-libs package locally
# 2. Running CI pipelines for testing and validation
#
# It first creates a base image with pre-cached dnf metadata,
# then builds both development and CI containers.

# Define image names
BASE_IMAGE="fedora:latest"     # The starting point - official Fedora image
CACHED_IMAGE="sts-base:latest" # Intermediate image with dnf cache
DEV_IMAGE="sts-dev:latest"     # Development container image
CI_IMAGE="sts-ci:latest"       # CI container image

# Flag to control building the CI image (default: disabled)
BUILD_CI=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --with-ci)
      BUILD_CI=1
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--with-ci]"
      exit 1
      ;;
  esac
done

# Change to the script's directory
cd "$(dirname "$0")"

# Step 1: Create an optimized base image with cached dnf metadata
echo "Creating optimized base image with dnf cache..."
# Remove any existing temporary container
podman rm -f fresh --time 0 2>/dev/null || true
# Create a new container with the latest fedora image
podman run -itd --name fresh --pull always "$BASE_IMAGE"
# Populate the dnf cache (this speeds up future package installs)
podman exec fresh dnf makecache
# Save the container with populated cache as a new image
podman commit fresh "$CACHED_IMAGE"
# Clean up the temporary container
podman rm -f fresh

# Step 2: Build the development container
echo "Building development container..."
podman build -t "$DEV_IMAGE" -f Containerfile .

# Step 3 (Optional): Build the CI container
if [ "$BUILD_CI" -eq 1 ]; then
  echo "Building CI container..."
  podman build -t "$CI_IMAGE" -f ci.Containerfile .

  echo -e "\nCI container built successfully!"
  echo "You can push this to your registry with:"
  echo "  podman push $CI_IMAGE quay.io/your-org/sts-ci:latest"
fi

# Print success message and usage instructions
echo -e "\nContainer build completed!"
echo -e "\nTo use the development container, you can run:"
echo "  * Run sts-libs unit tests: ./run.sh test"
echo "  * Get a shell:             ./run.sh shell"
echo
echo "NOTE: These containers are ONLY for sts-libs library development"
echo "      For developing actual tests that use sts-libs, use:"
echo "      tmt try fedora@container"
