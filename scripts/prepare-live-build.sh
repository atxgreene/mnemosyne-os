#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LB_DIR="$ROOT/iso/live-build"
INCLUDE_DIR="$LB_DIR/config/includes.chroot/opt/mnemosyne-os/source"

rm -rf "$INCLUDE_DIR"
mkdir -p "$INCLUDE_DIR"

rsync -a \
  --exclude '.git/' \
  --exclude '.venv/' \
  --exclude '.pytest_cache/' \
  --exclude '__pycache__/' \
  --exclude '.tmp-mnemosyne/' \
  --exclude 'iso/live-build/config/includes.chroot/' \
  --exclude 'iso/live-build/cache/' \
  --exclude 'iso/live-build/chroot/' \
  --exclude 'iso/live-build/binary/' \
  --exclude 'iso/live-build/live-image-*.iso' \
  "$ROOT/" "$INCLUDE_DIR/"

chmod +x "$INCLUDE_DIR/bin/mnemosyne" || true
chmod +x "$INCLUDE_DIR/packaging/install-mnemosyne-os.sh"
chmod +x "$INCLUDE_DIR/scripts"/*.sh || true
chmod +x "$LB_DIR/config/hooks/normal/010-install-mnemosyne.hook.chroot"

cat <<MSG
Prepared live-build source include:
  $INCLUDE_DIR

Next:
  cd "$LB_DIR"
  sudo lb clean --purge || true
  sudo lb config
  sudo lb build
MSG
