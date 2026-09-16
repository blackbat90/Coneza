#!/usr/bin/env bash
# ==============================================================================
# coneza Linux Edge Webserver & Phoenix Contact EZA Controller Installer
# Target Systems: Debian 11/12, Ubuntu 22.04/24.04 LTS, Phoenix Contact EPC Linux
# ==============================================================================

set -e

echo "=========================================================="
echo "    Installing coneza Edge Node on Linux"
echo "=========================================================="

# Check root privileges
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run this installation script as root (sudo ./install_linux.sh)"
  exit 1
fi

INSTALL_DIR="/opt/coneza"
SERVICE_USER="coneza"

echo "[1/5] Installing system prerequisites (Python, Tesseract OCR, Poppler)..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv tesseract-ocr poppler-utils net-tools

echo "[2/5] Creating dedicated service user '${SERVICE_USER}'..."
if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
    useradd -r -s /bin/false -d "${INSTALL_DIR}" "${SERVICE_USER}"
fi

echo "[3/5] Setting up deployment directory at ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"
cp -r . "${INSTALL_DIR}/"
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}"

echo "[4/5] Creating Python virtual environment..."
cd "${INSTALL_DIR}"
sudo -u "${SERVICE_USER}" python3 -m venv .venv
sudo -u "${SERVICE_USER}" "${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip -q
sudo -u "${SERVICE_USER}" "${INSTALL_DIR}/.venv/bin/pip" install -r requirements.txt -q

echo "[5/5] Generating systemd service unit /etc/systemd/system/coneza-edge.service..."
cat << 'EOF' > /etc/systemd/system/coneza-edge.service
[Unit]
Description=coneza Linux Edge Node & Phoenix Contact EZA Modbus Gateway
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=coneza
Group=coneza
WorkingDirectory=/opt/coneza
Environment="PATH=/opt/coneza/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONPATH=/opt/coneza"
Environment="EZA_CONTROLLER_HOST=127.0.0.1"
Environment="EZA_CONTROLLER_PORT=5502"
Environment="CONEZA_BACKEND_URL=http://192.168.10.10:8080"
Environment="START_EMBEDDED_SIMULATOR=true"
ExecStart=/opt/coneza/.venv/bin/python edge/main.py
Restart=always
RestartSec=5s
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable coneza-edge.service
systemctl restart coneza-edge.service

echo ""
echo "=========================================================="
echo " [SUCCESS] coneza Edge Node installed and started!"
echo " - Edge Webserver URL: http://$(hostname -I | awk '{print $1}'):8000"
echo " - Service Status:     systemctl status coneza-edge.service"
echo " - Live Logs:          journalctl -u coneza-edge.service -f"
echo "=========================================================="
