#!/bin/bash

# Script to build and publish latteries package to TestPyPI using uv

set -e  # Exit on any error

echo "🧪 Building and publishing latteries package to TestPyPI"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package with uv
echo "🔨 Building the package with uv..."
uv build

# Publish to TestPyPI with uv
echo "📤 Publishing to TestPyPI..."
echo "Note: Set UV_PUBLISH_TOKEN environment variable with your TestPyPI token"
echo "Or use --token flag. Get token at: https://test.pypi.org/manage/account/token/"
uv publish --index testpypi

echo "✅ Package published to TestPyPI successfully!"
echo "🧪 Test install with: pip install -i https://test.pypi.org/simple/ latteries"