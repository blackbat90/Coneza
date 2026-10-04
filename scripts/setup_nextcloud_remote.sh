#!/bin/bash
set -e

echo "=== 1. Preparing PostgreSQL for Nextcloud ==="
docker exec db psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='nextcloud'" | grep -q 1 || \
    docker exec db psql -U postgres -c "CREATE USER nextcloud WITH PASSWORD 'NextcloudSecure2026!';"

docker exec db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='nextcloud'" | grep -q 1 || \
    docker exec db psql -U postgres -c "CREATE DATABASE nextcloud OWNER nextcloud;"

docker exec db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nextcloud TO nextcloud;"
docker exec db psql -U postgres -c "ALTER DATABASE nextcloud OWNER TO nextcloud;"

echo "=== 2. Creating Nextcloud Directory Structure ==="
mkdir -p /srv/nextcloud/html
mkdir -p /srv/nextcloud/data
chown -R 33:33 /srv/nextcloud/html /srv/nextcloud/data
chmod -R 770 /srv/nextcloud/html /srv/nextcloud/data

echo "=== 3. Writing Nextcloud docker-compose.yml ==="
cat << 'EOF' > /srv/nextcloud/docker-compose.yml
services:
  nextcloud:
    image: nextcloud:30-apache
    container_name: nextcloud
    restart: unless-stopped
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_PASSWORD=NextcloudSecure2026!
      - NEXTCLOUD_ADMIN_USER=admin
      - NEXTCLOUD_ADMIN_PASSWORD=AdminCloudShare2026!
      - NEXTCLOUD_TRUSTED_DOMAINS=coneza.de www.coneza.de 195.90.215.204
      - OVERWRITEWEBROOT=/cloudshare
      - OVERWRITEHOST=coneza.de
      - OVERWRITEPROTOCOL=https
      - OVERWRITECLIURL=https://coneza.de/cloudshare
      - TRUSTED_PROXIES=172.18.0.0/16 195.90.215.204 coneza-web-fe
      - PHP_MEMORY_LIMIT=1024M
      - PHP_UPLOAD_LIMIT=10G
    volumes:
      - ./html:/var/www/html
      - ./data:/var/www/html/data
    networks:
      - coneza-net

networks:
  coneza-net:
    external: true
    name: coneza-web-fe_default
EOF

echo "=== 4. Starting Nextcloud Container ==="
cd /srv/nextcloud
docker compose down || true
docker compose up -d

echo "=== 5. Updating Nginx Configuration in /srv/Coneza-Web-FE/nginx/default.conf ==="
cat << 'EOF' > /srv/Coneza-Web-FE/nginx/default.conf
server {
    listen 80;
    listen [::]:80;

    server_name coneza.de www.coneza.de;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://coneza.de$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name coneza.de www.coneza.de;

    ssl_certificate /etc/letsencrypt/live/coneza.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/coneza.de/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;

    root /usr/share/nginx/html;
    index index.html;

    # coneza Management Portal & API
    location = /portal {
        return 301 /portal/;
    }

    location /portal/ {
        proxy_pass http://coneza-backend-server:8080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /portal;
        client_max_body_size 50M;
    }

    location /api/ {
        proxy_pass http://coneza-backend-server:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }

    # Nextcloud CloudShare (/cloudshare)
    location = /cloudshare {
        return 301 /cloudshare/;
    }

    location /.well-known/carddav {
        return 301 $scheme://$host/cloudshare/remote.php/dav;
    }

    location /.well-known/caldav {
        return 301 $scheme://$host/cloudshare/remote.php/dav;
    }

    location /cloudshare/ {
        proxy_pass http://nextcloud:80/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_redirect off;
        proxy_buffering off;
        client_max_body_size 10G;
        client_body_timeout 300s;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

echo "=== 6. Reloading Nginx ==="
docker exec coneza-web-fe nginx -t
docker exec coneza-web-fe nginx -s reload

echo "=== Setup Script Completed Successfully ==="
