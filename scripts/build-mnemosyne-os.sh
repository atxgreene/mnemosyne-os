#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper for Cubic/manual chroot installs.
# Preferred installer: packaging/install-mnemosyne-os.sh
# Expected source path inside the image: /opt/mnemosyne-os/source

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALLER="$REPO_DIR/packaging/install-mnemosyne-os.sh"

if [ ! -x "$INSTALLER" ]; then
  chmod +x "$INSTALLER"
fi

"$INSTALLER" --source "$REPO_DIR"

cat <<MSG

Cubic wrapper complete.

Source on OS: /opt/mnemosyne-os/source
Runtime data: /var/lib/mnemosyne
Service:      mnemosyne.service
API:          http://127.0.0.1:8765/health

Next checks inside the chroot or booted image:
  systemctl status mnemosyne --no-pager
  curl http://127.0.0.1:8765/health
  mnemosyne route "Deploy safely with security review" --json
MSG
