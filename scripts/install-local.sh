#!/bin/bash
set -e
echo "Installing Mnemosyne cognitive core..."

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

mkdir -p data

echo "\nInstallation complete."
echo "Run with: ./scripts/run-dev.sh"