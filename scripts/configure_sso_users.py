#!/usr/bin/env python3
"""
Configure SSO for s.saleem@coneza.de & w.ahmad@coneza.de
across Nextcloud (coneza.de/cloudshare) and Coneza Portal (coneza.de/portal)
with Mailcow OAuth2 integration.
"""

import sqlite3
import subprocess
import json
import os
import bcrypt

UNIFIED_PASSWORD = "ConezaSecure2026!"

print("=== 1. Setting up Portal Database Users ===")
db_path = "/var/lib/docker/volumes/coneza_backend_data/_data/coneza_backend.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Hash password
hashed_pw = bcrypt.hashpw(UNIFIED_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Check or insert s.saleem@coneza.de
cursor.execute("SELECT id, username, role FROM users WHERE email = 's.saleem@coneza.de' OR username = 's.saleem@coneza.de'")
user_saleem = cursor.fetchone()
if user_saleem:
    cursor.execute("UPDATE users SET hashed_password = ?, role = 'SUPER_ADMIN', must_change_password = 0 WHERE id = ?", (hashed_pw, user_saleem[0]))
    print(f"Updated s.saleem@coneza.de (ID {user_saleem[0]}) to SUPER_ADMIN")
else:
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, role, must_change_password, is_2fa_enabled) VALUES (?, ?, ?, 'SUPER_ADMIN', 0, 0)",
        ("s.saleem@coneza.de", "s.saleem@coneza.de", hashed_pw)
    )
    print("Inserted s.saleem@coneza.de as SUPER_ADMIN")

# Check or update w.ahmad@coneza.de
cursor.execute("SELECT id, username, role FROM users WHERE email = 'w.ahmad@coneza.de' OR username = 'w.ahmad@coneza.de'")
user_ahmad = cursor.fetchone()
if user_ahmad:
    cursor.execute("UPDATE users SET hashed_password = ?, role = 'SUPER_ADMIN', must_change_password = 0 WHERE id = ?", (hashed_pw, user_ahmad[0]))
    print(f"Updated w.ahmad@coneza.de (ID {user_ahmad[0]}) to SUPER_ADMIN")
else:
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, role, must_change_password, is_2fa_enabled) VALUES (?, ?, ?, 'SUPER_ADMIN', 0, 0)",
        ("w.ahmad@coneza.de", "w.ahmad@coneza.de", hashed_pw)
    )
    print("Inserted w.ahmad@coneza.de as SUPER_ADMIN")

conn.commit()
conn.close()

print("\n=== 2. Creating Nextcloud Users ===")
# Add s.saleem@coneza.de to Nextcloud
cmd_add_saleem = [
    "docker", "exec", "-e", f"OC_PASS={UNIFIED_PASSWORD}", "-u", "www-data", "nextcloud",
    "php", "occ", "user:add", "--password-from-env",
    "--display-name=Shehzad Saleem",
    "--email=s.saleem@coneza.de",
    "-g", "admin",
    "s.saleem@coneza.de"
]
res_saleem = subprocess.run(cmd_add_saleem, capture_output=True, text=True)
print("Nextcloud s.saleem@coneza.de:", res_saleem.stdout.strip() or res_saleem.stderr.strip())

# Add w.ahmad@coneza.de to Nextcloud
cmd_add_ahmad = [
    "docker", "exec", "-e", f"OC_PASS={UNIFIED_PASSWORD}", "-u", "www-data", "nextcloud",
    "php", "occ", "user:add", "--password-from-env",
    "--display-name=Wajheeh Ahmad",
    "--email=w.ahmad@coneza.de",
    "-g", "admin",
    "w.ahmad@coneza.de"
]
res_ahmad = subprocess.run(cmd_add_ahmad, capture_output=True, text=True)
print("Nextcloud w.ahmad@coneza.de:", res_ahmad.stdout.strip() or res_ahmad.stderr.strip())

# If users already existed, ensure password and email are set
for uid in ["s.saleem@coneza.de", "w.ahmad@coneza.de"]:
    subprocess.run([
        "docker", "exec", "-e", f"OC_PASS={UNIFIED_PASSWORD}", "-u", "www-data", "nextcloud",
        "php", "occ", "user:resetpassword", "--password-from-env", uid
    ], capture_output=True)
    subprocess.run([
        "docker", "exec", "-u", "www-data", "nextcloud",
        "php", "occ", "group:adduser", "admin", uid
    ], capture_output=True)

print("\n=== 3. Registering Mailcow OAuth2 Client ===")
# Query/Insert into Mailcow MySQL
CLIENT_ID = "nextcloud-cloudshare"
CLIENT_SECRET = "ConezaCloudSSO2026!"
REDIRECT_URI = "https://coneza.de/cloudshare/apps/sociallogin/custom_oauth2/mailcow"

sql_oauth = f"""
REPLACE INTO oauth_clients (client_id, client_secret, redirect_uri, grant_types, scope)
VALUES ('{CLIENT_ID}', '{CLIENT_SECRET}', '{REDIRECT_URI}', 'authorization_code', 'profile email openid');
"""

cmd_mysql = [
    "docker", "exec", "mailcowdockerized-mysql-mailcow-1",
    "mysql", "-u", "mailcow", "-pPayDdBzB7TqllruVekiA618iDEn0", "mailcow",
    "-e", sql_oauth
]
res_sql = subprocess.run(cmd_mysql, capture_output=True, text=True)
print("Mailcow OAuth Client Insert:", "SUCCESS" if res_sql.returncode == 0 else res_sql.stderr)

print("\n=== 4. Configuring Nextcloud Social Login (Mailcow OAuth2 Provider) ===")
# Enable Social Login and configure Mailcow Custom OAuth2
social_config = {
    "custom_oauth2": [
        {
            "name": "mailcow",
            "title": "Coneza SSO (Mail-Konto)",
            "authorizeUrl": "https://coneza.de/mail/oauth/authorize",
            "tokenUrl": "https://coneza.de/mail/oauth/token",
            "profileUrl": "https://coneza.de/mail/oauth/profile",
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
cmd_social = [
    "docker", "exec", "-u", "www-data", "nextcloud",
    "php", "occ", "config:app:set", "sociallogin", "custom_providers",
    "--value", social_json
]
res_soc = subprocess.run(cmd_social, capture_output=True, text=True)
print("Social Login Config:", res_soc.stdout.strip() or res_soc.stderr.strip())

# Allow auto-creation and prevent disabling local login
subprocess.run(["docker", "exec", "-u", "www-data", "nextcloud", "php", "occ", "config:app:set", "sociallogin", "allow_login_connect", "--value", "1"])
subprocess.run(["docker", "exec", "-u", "www-data", "nextcloud", "php", "occ", "config:app:set", "sociallogin", "prevent_create_email_exists", "--value", "0"])

print("\n=== 5. Updating Nginx with /mail/ Proxy for OAuth2 ===")
nginx_conf_path = "/srv/Coneza-Web-FE/nginx/default.conf"
with open(nginx_conf_path, "r") as f:
    conf = f.read()

if "location /mail/" not in conf:
    mail_block = """
    # Mailcow OAuth2 & API Proxy for SSO
    location /mail/ {
        proxy_pass https://172.18.0.1:8443/;
        proxy_ssl_verify off;
        proxy_set_header Host mail.coneza.de;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }
"""
    # Insert right before the last closing brace
    last_brace = conf.rfind("}")
    if last_brace != -1:
        new_conf = conf[:last_brace] + mail_block + "\n}\n"
        with open(nginx_conf_path, "w") as f:
            f.write(new_conf)
        print("Added /mail/ location block to Nginx configuration.")
        subprocess.run(["docker", "exec", "coneza-web-fe", "nginx", "-t"], check=True)
        subprocess.run(["docker", "exec", "coneza-web-fe", "nginx", "-s", "reload"], check=True)
        print("Nginx reloaded successfully.")
else:
    print("/mail/ proxy block already exists in Nginx.")

print("\n=== SSO Configuration Completed Successfully! ===")
