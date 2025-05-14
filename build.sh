#!/bin/bash

# Exit on error
set -e

# Get the absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create RPM build directories
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create a temporary build directory
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT

echo "Copying files to build directory..."

# Copy files to build directory
cp -r "$PROJECT_DIR/api" "$BUILD_DIR/"
cp "$PROJECT_DIR/packaging/artifact-api-local.service" "$BUILD_DIR/"
cp "$PROJECT_DIR/packaging/artifact-api-local.spec" ~/rpmbuild/SPECS/

# Verify files exist
if [ ! -f "$BUILD_DIR/artifact-api-local.service" ]; then
    echo "Error: Service file not found at $BUILD_DIR/artifact-api-local.service"
    exit 1
fi

if [ ! -f "$HOME/rpmbuild/SPECS/artifact-api-local.spec" ]; then
    echo "Error: Spec file not found at $HOME/rpmbuild/SPECS/artifact-api-local.spec"
    exit 1
fi

# Copy files to RPM build directory
cp -r "$BUILD_DIR"/* ~/rpmbuild/BUILD/

echo "Building RPM..."
# Build the RPM
rpmbuild -bb ~/rpmbuild/SPECS/artifact-api-local.spec

echo "RPM built successfully!"
echo "You can find the RPM at: ~/rpmbuild/RPMS/noarch/artifact-api-local-1.0.0-1.el10.noarch.rpm"
echo ""
echo "To install the service, run:"
echo "sudo rpm -ivh ~/rpmbuild/RPMS/noarch/artifact-api-local-1.0.0-1.el10.noarch.rpm" 