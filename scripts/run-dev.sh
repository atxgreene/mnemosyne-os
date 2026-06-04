#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .venv/Scripts/activate ]; then
  source .venv/Scripts/activate
elif [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
python scripts/load-starter-content.py
printf 'Dashboard: file://%s/dashboard/mnemosyne-panels.html\n' "$PWD"
python -m uvicorn mnemosyne.services.api_server:app --host 127.0.0.1 --port 8765 --reload
