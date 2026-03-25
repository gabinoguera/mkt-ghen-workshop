#!/usr/bin/env bash
# Bootstrap script: creates Python 3.11 venv and installs dependencies
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="/opt/homebrew/bin/python3.11"

if ! command -v "$PYTHON" &>/dev/null; then
    echo "ERROR: Python 3.11 not found at $PYTHON"
    echo "Install with: brew install python@3.11"
    exit 1
fi

if [ -d "$VENV_DIR" ]; then
    echo "venv already exists at $VENV_DIR"
else
    echo "Creating venv with $($PYTHON --version)..."
    "$PYTHON" -m venv "$VENV_DIR"
    echo "venv created."
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
echo "Done. Activate with: source $VENV_DIR/bin/activate"
