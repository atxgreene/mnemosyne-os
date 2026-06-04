#!/usr/bin/env bash
set -euo pipefail

# Run inside a Cubic Ubuntu chroot after copying this repo to /opt/mnemosyne-os,
# or use as a readable checklist for the eventual custom ISO build.
REPO_DIR="${MNEMOSYNE_OS_REPO:-/opt/mnemosyne-os}"
INSTALL_DIR="/opt/mnemosyne-os"
SERVICE_USER="mnemosyne"

apt-get update
apt-get install -y python3 python3-venv python3-pip curl git ca-certificates

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir /var/lib/mnemosyne --shell /usr/sbin/nologin "$SERVICE_USER"
fi

mkdir -p "$INSTALL_DIR"
if [ "$REPO_DIR" != "$INSTALL_DIR" ]; then
  cp -a "$REPO_DIR"/. "$INSTALL_DIR"/
fi

cd "$INSTALL_DIR"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
MNEMOSYNE_HOME=/var/lib/mnemosyne python scripts/load-starter-content.py
chown -R "$SERVICE_USER:$SERVICE_USER" /var/lib/mnemosyne "$INSTALL_DIR"

cat >/etc/systemd/system/mnemosyne.service <<EOF
[Unit]
Description=Mnemosyne OS Cognitive Core
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=MNEMOSYNE_HOME=/var/lib/mnemosyne
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python -m uvicorn mnemosyne.services.api_server:app --host 0.0.0.0 --port 8765
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl enable mnemosyne.service

cat >/usr/local/bin/mnemosyne <<EOF
#!/usr/bin/env bash
cd $INSTALL_DIR
export PYTHONPATH=$INSTALL_DIR
exec $INSTALL_DIR/.venv/bin/python $INSTALL_DIR/bin/mnemosyne "\$@"
EOF
chmod +x /usr/local/bin/mnemosyne

cat >/usr/share/applications/mnemosyne-dashboard.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Mnemosyne Dashboard
Comment=Open the Mnemosyne OS memory graph dashboard
Exec=xdg-open file://$INSTALL_DIR/dashboard/mnemosyne-panels.html
Icon=applications-science
Terminal=false
Categories=Utility;Office;Science;
EOF

printf 'Mnemosyne OS scaffold installed. Service enabled on port 8765.\n'
