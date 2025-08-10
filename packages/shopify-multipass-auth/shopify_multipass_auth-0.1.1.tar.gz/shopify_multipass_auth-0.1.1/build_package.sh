#!/bin/bash

# Build and publish script for shopify-multipass-auth package

set -e

echo "🔨 Building shopify-multipass-auth package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install build twine

# Build the package
echo "🏗️  Building package..."
python -m build

# Check the package
echo "✅ Checking package..."
python -m twine check dist/*

echo "📋 Package contents:"
ls -la dist/

echo "✨ Build complete!"
echo ""
echo "To publish to PyPI:"
echo "  Test PyPI: python -m twine upload --repository testpypi dist/*"
echo "  PyPI:      python -m twine upload dist/*"
echo ""
echo "To install locally:"
echo "  pip install dist/*.whl"
