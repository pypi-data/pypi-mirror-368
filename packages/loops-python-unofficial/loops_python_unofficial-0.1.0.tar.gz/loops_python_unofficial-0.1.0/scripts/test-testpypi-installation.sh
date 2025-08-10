#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="test-env"
PACKAGE="loops-python-unofficial==0.1.0"
TEST_INDEX="https://test.pypi.org/simple/"
PYPI_INDEX="https://pypi.org/simple"

echo "Creating virtual environment: $ENV_NAME"
python -m venv "$ENV_NAME"

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source "$ENV_NAME/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing $PACKAGE from TestPyPI with deps from PyPI if needed..."
pip install \
  --index-url "$TEST_INDEX" \
  --extra-index-url "$PYPI_INDEX" \
  "$PACKAGE"

echo "Dropping into Python REPL for a quick test. Type 'exit()' or Ctrl+D to quit."
python

echo "Cleaning up..."
deactivate
rm -rf "$ENV_NAME"
echo "Done."
