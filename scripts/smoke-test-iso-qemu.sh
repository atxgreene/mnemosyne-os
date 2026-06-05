#!/usr/bin/env bash
set -euo pipefail

ISO_PATH="${1:-iso/live-build/live-image-amd64.hybrid.iso}"
TIMEOUT_SECONDS="${MNEMOSYNE_QEMU_TIMEOUT_SECONDS:-900}"
LOG_PATH="${MNEMOSYNE_QEMU_SERIAL_LOG:-qemu-smoke-serial.log}"
ACCEL="tcg"
if [ -e /dev/kvm ] && [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
  ACCEL="kvm:tcg"
fi

if [ ! -f "$ISO_PATH" ]; then
  echo "ISO not found: $ISO_PATH" >&2
  exit 2
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "qemu-system-x86_64 not found" >&2
  exit 2
fi

rm -f "$LOG_PATH"
touch "$LOG_PATH"

echo "Starting QEMU smoke test: iso=${ISO_PATH} timeout=${TIMEOUT_SECONDS}s accel=${ACCEL} log=${LOG_PATH}"

qemu-system-x86_64 \
  -machine accel="$ACCEL" \
  -m 2048 \
  -smp 2 \
  -cdrom "$ISO_PATH" \
  -boot d \
  -display none \
  -serial file:"$LOG_PATH" \
  -no-reboot \
  -netdev user,id=net0 \
  -device e1000,netdev=net0 &
QEMU_PID=$!

cleanup() {
  if kill -0 "$QEMU_PID" >/dev/null 2>&1; then
    kill "$QEMU_PID" >/dev/null 2>&1 || true
    wait "$QEMU_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

DEADLINE=$((SECONDS + TIMEOUT_SECONDS))
while [ "$SECONDS" -lt "$DEADLINE" ]; do
  if grep -q "MNEMOSYNE_ISO_SMOKE: PASS" "$LOG_PATH"; then
    echo "QEMU smoke test passed"
    tail -80 "$LOG_PATH" || true
    exit 0
  fi
  if grep -q "MNEMOSYNE_ISO_SMOKE: FAIL" "$LOG_PATH"; then
    echo "QEMU smoke test failed inside guest" >&2
    tail -160 "$LOG_PATH" >&2 || true
    exit 1
  fi
  if ! kill -0 "$QEMU_PID" >/dev/null 2>&1; then
    echo "QEMU exited before smoke marker" >&2
    tail -160 "$LOG_PATH" >&2 || true
    exit 1
  fi
  sleep 5
done

echo "Timed out waiting for QEMU smoke marker after ${TIMEOUT_SECONDS}s" >&2
tail -200 "$LOG_PATH" >&2 || true
exit 1
