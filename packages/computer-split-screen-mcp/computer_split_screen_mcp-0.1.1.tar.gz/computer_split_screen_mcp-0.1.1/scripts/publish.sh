#!/bin/bash

# Publish script for computer-split-screen-mcp
# This script builds and publishes the package to PyPI

set -e

echo "🚀 Building and publishing computer-split-screen-mcp..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "🔨 Building package..."
python3 -m build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed. dist/ directory not created."
    exit 1
fi

echo "✅ Package built successfully!"

# Show what was built
echo "📦 Built packages:"
ls -la dist/

# Ask user if they want to publish
echo ""
read -p "Do you want to publish to PyPI? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Publishing to PyPI..."
    
    # Check if twine is installed
    if ! command -v twine &> /dev/null; then
        echo "📦 Installing twine..."
        pip install twine
    fi
    
    # Upload to PyPI
    twine upload dist/*
    
    echo "✅ Package published successfully!"
    echo "🎉 You can now install it with: pip install computer-split-screen-mcp"
else
    echo "📦 Package built but not published."
    echo "To publish later, run: twine upload dist/*"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Test the package: pip install computer-split-screen-mcp"
echo "2. Test MCP integration with your client"
echo "3. Update version in pyproject.toml for next release"
