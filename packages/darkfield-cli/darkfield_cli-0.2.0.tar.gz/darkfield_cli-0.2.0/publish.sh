#!/bin/bash

echo "🚀 Publishing darkfield CLI to PyPI"
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Install build tools
echo "📦 Installing build tools..."
pip install --upgrade build twine

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "✅ Checking package..."
twine check dist/*

# Upload to TestPyPI first (optional)
echo ""
echo "📤 Upload to TestPyPI first? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    twine upload --repository testpypi dist/*
    echo ""
    echo "Test with: pip install --index-url https://test.pypi.org/simple/ darkfield-cli"
    echo ""
fi

# Upload to PyPI
echo "📤 Upload to PyPI? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    twine upload dist/*
    echo ""
    echo "✅ Published! Install with: pip install darkfield-cli"
fi