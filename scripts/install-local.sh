#!/bin/bash
set -euo pipefail

echo "Installing Mnemosyne cognitive core..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MNEMOSYNE_PYTHON="${MNEMOSYNE_PYTHON:-python3}"
cd "$REPO_ROOT"

"$MNEMOSYNE_PYTHON" "$SCRIPT_DIR/check-python-runtime.py"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    "$MNEMOSYNE_PYTHON" -m venv .venv
fi

# Reject a stale venv made by an unsupported interpreter before invoking pip.
".venv/bin/python" "$SCRIPT_DIR/check-python-runtime.py"

source .venv/bin/activate
".venv/bin/python" -m pip install --require-hashes -r requirements.txt

mkdir -p data

printf '\nInstallation complete.\n'
echo "Run with: ./scripts/run-dev.sh"
