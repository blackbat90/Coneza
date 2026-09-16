#!/usr/bin/env bash
# ==============================================================================
# coneza Central Backend - Public Docker Deployment Script
# Configured for Custom Port (Default: 9080, avoiding 80, 443, and 8080)
# ==============================================================================

set -e

PORT="${BACKEND_PORT:-9080}"

echo "=========================================================="
echo "    Deploying coneza Central Backend via Docker"
echo "    Target Port: ${PORT} (Avoiding 80, 443, 8080)"
echo "=========================================================="

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker not detected. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm -f get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "[+] Docker installed successfully."
fi

# Ensure docker compose plugin is available
if ! docker compose version >/dev/null 2>&1; then
    echo "[!] Docker Compose plugin missing. Installing docker-compose-plugin..."
    apt-get update -qq && apt-get install -y -qq docker-compose-plugin
fi

# Check if chosen port is available
if command -v netstat >/dev/null 2>&1 || command -v ss >/dev/null 2>&1; then
    if ss -tuln | grep -q ":${PORT} "; then
        echo "[WARNING] Port ${PORT} appears to be in use. Please specify another port:"
        echo "Example: BACKEND_PORT=9090 sudo ./deploy_docker_backend.sh"
        exit 1
    fi
fi

# Setup .env if missing
if [ ! -f ".env" ]; then
    echo "[+] Creating .env file from template..."
    cp .env.example .env
    sed -i "s/BACKEND_PORT=9080/BACKEND_PORT=${PORT}/g" .env
fi

# Build and start container
echo "[+] Building and starting coneza-backend-server container on port ${PORT}..."
export BACKEND_PORT="${PORT}"
docker compose -f docker/docker-compose.backend.yml up -d --build

# Open Firewall (UFW) if active
if command -v ufw >/dev/null 2>&1; then
    if ufw status | grep -q "Status: active"; then
        echo "[+] Allowing port ${PORT}/tcp through UFW firewall..."
        ufw allow "${PORT}/tcp"
    fi
fi

# Wait for container startup
echo "[+] Waiting for container health check..."
sleep 4

PUBLIC_IP=$(curl -s https://api.ipify.org || hostname -I | awk '{print $1}')

echo ""
echo "=========================================================="
echo " [SUCCESS] coneza Backend Container is running!"
echo " - Public Web Dashboard: http://${PUBLIC_IP}:${PORT}"
echo " - Default Super User:    admin / conezaAdmin2026!"
echo " - Container Name:        coneza-backend-server"
echo " - View Logs:             docker logs -f coneza-backend-server"
echo " - Stop Container:        docker compose -f docker/docker-compose.backend.yml down"
echo "=========================================================="
