import subprocess
import json
import secrets

remote_script = """
import subprocess
import json
import secrets

api_key = "CONEZA-ADMIN-API-" + secrets.token_hex(16)
new_pw = "ConezaSecure2026!"
user = "s.saleem@coneza.de"

# Get MySQL password
db_pw = subprocess.check_output(
    "docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2",
    shell=True, text=True
).strip()

# Configure API key in MariaDB
sql = f\"\"\"
DELETE FROM api WHERE api_key LIKE 'CONEZA-%';
INSERT INTO api (api_key, allow_from, skip_ip_check, access, active)
VALUES ('{api_key}', '0.0.0.0/0', 1, 'rw', 1);
\"\"\"
cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", sql]
subprocess.run(cmd, check=True)
print("Configured API key:", api_key)

# Call Mailcow API to update mailbox password
payload = {
    "items": [user],
    "attr": {
        "password": new_pw,
        "password2": new_pw,
        "force_pw_update": "0"
    }
}

curl_cmd = [
    "curl", "-k", "-s", "-X", "POST",
    "-H", "Content-Type: application/json",
    "-H", f"X-API-Key: {api_key}",
    "-d", json.dumps(payload),
    "https://127.0.0.1:8443/api/v1/edit/mailbox"
]
res = subprocess.check_output(curl_cmd, text=True)
print("API Response:", res)

# Flush Redis cache in redis-mailcow
subprocess.run(["docker", "exec", "mailcowdockerized-redis-mailcow-1", "redis-cli", "FLUSHALL"], check=True)
print("Flushed Redis cache")

# Test authentication via doveadm
test_cmd = ["docker", "exec", "mailcowdockerized-dovecot-mailcow-1", "doveadm", "auth", "test", user, new_pw]
test_res = subprocess.run(test_cmd, capture_output=True, text=True)
print("Auth test returncode:", test_res.returncode)
print("Auth test stdout:", test_res.stdout)
print("Auth test stderr:", test_res.stderr)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_set_pw_api.py", "w") as f:
    f.write(remote_script)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_set_pw_api.py", "root@195.90.215.204:/tmp/set_pw_api.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/set_pw_api.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
