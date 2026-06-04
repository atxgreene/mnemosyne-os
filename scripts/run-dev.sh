#!/bin/bash
set -e

echo "Starting Mnemosyne development server..."
source .venv/bin/activate || true

uvicorn mnemosyne.services.api_server:app --reload --host 0.0.0.0 --port 8765