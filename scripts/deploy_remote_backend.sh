#!/usr/bin/env bash
# ==============================================================================
# coneza Central Backend - Public Webserver Deployment Script
# Target: Ubuntu 22.04 / 24.04 LTS, Debian 11 / 12 (VPS / Cloud VM)
# ==============================================================================

set -e

echo "=========================================================="
echo "    Deploying coneza Central Backend on Public Server"
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root: sudo ./deploy_remote_backend.sh"
  exit 1
fi

APP_DIR="/opt/coneza-backend"
APP_USER="coneza"

echo "[1/6] Updating system & installing prerequisites..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx curl ufw

echo "[2/6] Creating service user '${APP_USER}'..."
if ! id -u "${APP_USER}" >/dev/null 2>&1; then
    useradd -r -m -s /bin/bash "${APP_USER}"
fi

echo "[3/6] Setting up application directory at ${APP_DIR}..."
mkdir -p "${APP_DIR}"

# If repo not cloned yet, copy current dir
if [ -d "./backend" ]; then
    cp -r . "${APP_DIR}/"
else
    echo "Copying files to ${APP_DIR}..."
fi

chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

echo "[4/6] Setting up Python virtual environment..."
cd "${APP_DIR}"
sudo -u "${APP_USER}" python3 -m venv .venv
sudo -u "${APP_USER}" "${APP_DIR}/.venv/bin/pip" install --upgrade pip -q
sudo -u "${APP_USER}" "${APP_DIR}/.venv/bin/pip" install -r requirements.txt -q

echo "[5/6] Creating systemd service unit /etc/systemd/system/coneza-backend.service..."
cat << EOF > /etc/systemd/system/coneza-backend.service
[Unit]
Description=coneza Central Backend & Fleet Management Server
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONPATH=${APP_DIR}"
Environment="CONEZA_JWT_SECRET=coneza-super-secret-jwt-key-2026-vde4110"
# Uncomment and set your Gemini API key:
# Environment="GEMINI_API_KEY=your-api-key-here"
ExecStart=${APP_DIR}/.venv/bin/python backend/main.py
Restart=always
RestartSec=5s
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable coneza-backend.service
systemctl restart coneza-backend.service

echo "[6/6] Configuring Nginx Reverse Proxy..."
cat << 'EOF' > /etc/nginx/sites-available/coneza
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -sf /etc/nginx/sites-available/coneza /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Configure Firewall (UFW)
if ufw status | grep -q "Status: active"; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
fi

PUBLIC_IP=$(curl -s https://api.ipify.org || hostname -I | awk '{print $1}')

echo ""
echo "=========================================================="
echo " [SUCCESS] coneza Central Backend is now live!"
echo " - Public URL:      http://${PUBLIC_IP}"
echo " - Service Status:  systemctl status coneza-backend.service"
echo " - Service Logs:    journalctl -u coneza-backend.service -f"
echo " - Super User:      admin / conezaAdmin2026!"
echo ""
echo " To enable SSL (HTTPS with free Let's Encrypt):"
echo "   certbot --nginx -d your-domain.com"
echo "=========================================================="
