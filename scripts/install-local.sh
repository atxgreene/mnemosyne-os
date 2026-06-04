#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
if [ -f .venv/Scripts/activate ]; then
  # Windows Git Bash
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/load-starter-content.py
printf '\nMnemosyne OS installed locally.\n'
printf 'Run: ./scripts/run-dev.sh\n'
printf 'CLI: python bin/mnemosyne search memory\n'
