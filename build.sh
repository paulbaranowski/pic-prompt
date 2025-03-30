#!/bin/bash
set -e  # Exit on any error

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Please provide a version number (e.g. ./build.sh 1.1.17)"
    exit 1
fi

NEW_VERSION=$1

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Clean up previous builds
rm -rf dist/ build/ src/*.egg-info/

# Update version in pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Install/upgrade build tools
uv pip install --upgrade build twine

# Run tests
uv pip install -e ".[test]"
pytest

# Build the package
python -m build

# Upload to PyPI (will prompt for credentials)
python -m twine upload dist/*

echo "Successfully published version $NEW_VERSION to PyPI" 