#!/usr/bin/env bash
set -euo pipefail

SOURCE_ARG=""
ENABLE_SERVICE=1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --source)
      SOURCE_ARG="${2:-}"
      shift 2
      ;;
    --no-enable)
      ENABLE_SERVICE=0
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo $0 --source /path/to/mnemosyne-os" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_INPUT_RAW="${SOURCE_ARG:-$REPO_ROOT}"
SOURCE_INPUT="$(realpath "$SOURCE_INPUT_RAW")"
SOURCE_DIR=/opt/mnemosyne-os/source
VENV_DIR=/opt/mnemosyne-os/.venv
DATA_DIR=/var/lib/mnemosyne
SERVICE_SRC="$SOURCE_INPUT/packaging/systemd/mnemosyne.service"

if [ ! -f "$SOURCE_INPUT/requirements.txt" ] || [ ! -d "$SOURCE_INPUT/mnemosyne" ]; then
  echo "Source path does not look like mnemosyne-os: $SOURCE_INPUT" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 \
  python3-venv \
  python3-pip \
  rsync \
  curl \
  ca-certificates

if ! id mnemosyne >/dev/null 2>&1; then
  useradd --system --home "$DATA_DIR" --create-home --shell /usr/sbin/nologin mnemosyne
fi

mkdir -p /opt/mnemosyne-os "$DATA_DIR"
if [ "$SOURCE_INPUT" != "$SOURCE_DIR" ]; then
  rsync -a --delete \
    --exclude '.git/' \
    --exclude '.venv/' \
    --exclude '.pytest_cache/' \
    --exclude '__pycache__/' \
    --exclude '.tmp-mnemosyne/' \
    "$SOURCE_INPUT/" "$SOURCE_DIR/"
else
  echo "Source already staged at $SOURCE_DIR; skipping self-rsync."
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SOURCE_DIR/requirements.txt"

MNEMOSYNE_HOME="$DATA_DIR" "$VENV_DIR/bin/python" "$SOURCE_DIR/scripts/load-starter-content.py"

ln -sf "$SOURCE_DIR/bin/mnemosyne" /usr/local/bin/mnemosyne
chmod +x "$SOURCE_DIR/bin/mnemosyne"
chmod +x "$SOURCE_DIR/scripts"/*.sh

install -D -m 0644 "$SERVICE_SRC" /etc/systemd/system/mnemosyne.service
chown -R mnemosyne:mnemosyne "$DATA_DIR"
chown -R root:root /opt/mnemosyne-os

systemctl daemon-reload
if [ "$ENABLE_SERVICE" -eq 1 ]; then
  systemctl enable mnemosyne.service
  systemctl restart mnemosyne.service || true
fi

cat <<MSG
Mnemosyne OS userspace installed.

Source:       $SOURCE_DIR
Virtualenv:   $VENV_DIR
Runtime data: $DATA_DIR
CLI:          /usr/local/bin/mnemosyne
Service:      mnemosyne.service
API:          http://127.0.0.1:8765/health

Verify with:
  systemctl status mnemosyne --no-pager
  curl http://127.0.0.1:8765/health
  mnemosyne search Mnemosyne --json
MSG
