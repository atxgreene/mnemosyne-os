#!/bin/bash
set -e

echo "Starting Mnemosyne development server..."
source .venv/bin/activate || true

uvicorn mnemosyne.services.api_server:app --reload --host 127.0.0.1 --port 8765