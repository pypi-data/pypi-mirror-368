#!/bin/bash
# Build script for passive-agent package

echo "Building passive-agent package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

echo "Build complete! Package files are in dist/"
echo ""
echo "To publish to PyPI, run:"
echo "  uv publish"
echo ""
echo "Or to test locally:"
echo "  pip install dist/passive_agent-*.whl"