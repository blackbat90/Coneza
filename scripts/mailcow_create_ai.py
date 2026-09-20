import subprocess
import json
import secrets
import string

def gen_password(length=20):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(length))

def run_remote_script(script: str):
    full_cmd = ["ssh", "root@195.90.215.204", "bash -s"]
    res = subprocess.run(full_cmd, input=script, capture_output=True, text=True, encoding="utf-8")
    return res.stdout, res.stderr, res.returncode

def main():
    # Use API key containing only a-zA-Z0-9-
    api_key = "CONEZA-AI-API-KEY-" + secrets.token_hex(16)
    ai_password = gen_password(24)
    print(f"Generated Mailbox Password: {ai_password}")
    print(f"Using API Key: {api_key}")

    # 1. Update API table
    setup_script = f"""
docker exec mailcowdockerized-mysql-mailcow-1 mysql -u root -pDdHDLx2fE2WzW4IeG8bqNDnNDtNT mailcow << 'SQLEOF'
DELETE FROM api;
INSERT INTO api (api_key, allow_from, skip_ip_check, access, active)
VALUES ('{api_key}', '0.0.0.0/0', 1, 'rw', 1);
SQLEOF
"""
    stdout, stderr, rc = run_remote_script(setup_script)
    if rc != 0:
        print("Failed to configure API key in DB:", stderr)
        return
    print("API key successfully configured in MariaDB.")

    # 2. Test API
    test_script = f"""
curl -k -s -H "X-API-Key: {api_key}" https://127.0.0.1:8443/api/v1/get/domain/coneza.de
"""
    stdout, stderr, rc = run_remote_script(test_script)
    print("Domain query response:", stdout)

    # 3. Create ai@coneza.de
    payload = json.dumps({
        "active": "1",
        "domain": "coneza.de",
        "local_part": "ai",
        "name": "Coneza AI Assistant",
        "password": ai_password,
        "password2": ai_password,
        "quota": "10240",
        "force_pw_update": "0",
        "force_tfa": "0"
    })

    create_script = f"""
curl -k -s -X POST -H "Content-Type: application/json" -H "X-API-Key: {api_key}" \
  -d '{payload}' \
  https://127.0.0.1:8443/api/v1/add/mailbox
"""
    stdout, stderr, rc = run_remote_script(create_script)
    print("Mailbox creation response:", stdout)

    # 4. Check user in Dovecot
    check_script = "docker exec mailcowdockerized-dovecot-mailcow-1 doveadm user ai@coneza.de"
    stdout, stderr, rc = run_remote_script(check_script)
    print("Dovecot lookup:", stdout)

    # 5. Save credentials
    with open("mailcow_ai_credentials.json", "w") as f:
        json.dump({
            "email": "ai@coneza.de",
            "password": ai_password,
            "api_key": api_key,
            "mailcow_url": "https://mail.coneza.de:8443"
        }, f, indent=2)
    print("Saved credentials to mailcow_ai_credentials.json")


if __name__ == "__main__":
    main()
