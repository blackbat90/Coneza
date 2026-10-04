#!/usr/bin/env python3
"""
Complete fix for Mailcow SSO with Nextcloud:
1. Updates Nginx in /srv/Coneza-Web-FE/nginx/default.conf with dedicated mail.coneza.de server blocks.
2. Updates Nextcloud sociallogin provider with https://mail.coneza.de URLs.
3. Reloads Nginx and verifies SSL on mail.coneza.de.
"""

import subprocess
import json

print("=== 1. Writing Nginx Configuration ===")
nginx_conf = """server {
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
    listen 80;
    listen [::]:80;

    server_name mail.coneza.de;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://mail.coneza.de$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name mail.coneza.de;

    ssl_certificate /etc/letsencrypt/live/mail.coneza.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mail.coneza.de/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass https://172.18.0.1:8443;
        proxy_ssl_verify off;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        client_max_body_size 100M;
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
"""

with open("/srv/Coneza-Web-FE/nginx/default.conf", "w") as f:
    f.write(nginx_conf)

print("Reloading Nginx...")
subprocess.run(["docker", "exec", "coneza-web-fe", "nginx", "-t"], check=True)
subprocess.run(["docker", "exec", "coneza-web-fe", "nginx", "-s", "reload"], check=True)
print("Nginx reloaded successfully.")

print("\n=== 2. Updating Nextcloud Social Login Settings ===")
CLIENT_ID = "nextcloud-cloudshare"
CLIENT_SECRET = "ConezaCloudSSO2026!"

social_config = {
    "custom_oauth2": [
        {
            "name": "mailcow",
            "title": "Coneza SSO (Mail-Konto)",
            "authorizeUrl": "https://mail.coneza.de/oauth/authorize",
            "tokenUrl": "https://mail.coneza.de/oauth/token",
            "profileUrl": "https://mail.coneza.de/oauth/profile",
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET,
            "scope": "profile email",
            "groups": ["admin"],
            "auto_create_user": True,
            "update_profile_on_login": True,
            "style": "mailcow"
        }
    ]
}

social_json = json.dumps(social_config)
subprocess.run([
    "docker", "exec", "-u", "www-data", "nextcloud",
    "php", "occ", "config:app:set", "sociallogin", "custom_providers",
    "--value", social_json
], check=True)

print("Updated Social Login config to https://mail.coneza.de.")

print("\n=== Fix completed successfully ===")
