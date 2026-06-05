#!/usr/bin/env bash
set -euo pipefail

SERIAL_DEVICE=/dev/ttyS0
MARKER_PREFIX=MNEMOSYNE_ISO_SMOKE

emit() {
  local message="$*"
  echo "${MARKER_PREFIX}: ${message}"
  if [ -w "$SERIAL_DEVICE" ]; then
    echo "${MARKER_PREFIX}: ${message}" > "$SERIAL_DEVICE"
  fi
}

emit "START"

for attempt in $(seq 1 90); do
  if curl --fail --silent --show-error http://127.0.0.1:8765/health >/tmp/mnemosyne-health.json; then
    emit "HEALTH_OK attempt=${attempt}"
    break
  fi
  sleep 2
  if [ "$attempt" -eq 90 ]; then
    emit "FAIL health_timeout"
    exit 1
  fi
done

if ! /usr/local/bin/mnemosyne search Mnemosyne --json >/tmp/mnemosyne-cli-search.json; then
  emit "FAIL cli_search"
  exit 1
fi
emit "CLI_OK"

if ! systemctl is-active --quiet mnemosyne.service; then
  emit "FAIL service_not_active"
  systemctl status mnemosyne.service --no-pager || true
  exit 1
fi
emit "SERVICE_OK"

emit "PASS"
