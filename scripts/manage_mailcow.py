import subprocess
import json
import ssl
import urllib.request
import urllib.error

def run_remote_ssh(command: str):
    clean_command = command.replace('\r\n', '\n').strip() + '\n'
    p = subprocess.Popen(['ssh', 'root@195.90.215.204', 'bash -s'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(input=clean_command)
    return out, err, p.returncode


def update_api_key():
    api_key = 'CONEZA-AI-API-KEY-e60442a8167b243274f552a97f106319'
    cmd = f"""
docker exec mailcowdockerized-mysql-mailcow-1 mysql -u root -pDdHDLx2fE2WzW4IeG8bqNDnNDtNT mailcow -e "DELETE FROM api; INSERT INTO api (api_key, allow_from, skip_ip_check, access, active) VALUES ('{api_key}', '0.0.0.0/0', 1, 'rw', 1);"
docker exec mailcowdockerized-mysql-mailcow-1 mysql -u root -pDdHDLx2fE2WzW4IeG8bqNDnNDtNT mailcow -e "SELECT * FROM api;"
"""
    out, err, rc = run_remote_ssh(cmd)
    print("Updated API Table:\n", out)
    if err:
        print("ERR:", err)

def run_setup():
    cmd = "python3 /tmp/setup_ai.py"
    out, err, rc = run_remote_ssh(cmd)
    print("Setup output:\n", out)
    if err:
        print("Setup ERR:\n", err)

def check_mailbox():
    cmd = "docker exec mailcowdockerized-dovecot-mailcow-1 doveadm user ai@coneza.de"
    out, err, rc = run_remote_ssh(cmd)
    print("Dovecot check:\n", out)

def check_emails():
    cmd = """
echo "=== DOVEADM SEARCH ==="
docker exec mailcowdockerized-dovecot-mailcow-1 doveadm search -u ai@coneza.de mailbox INBOX all

echo "=== MAILDIR CONTENTS ==="
ls -la /srv/mail-coneza/mailcow/data/vmail/coneza.de/ai/Maildir/new/ 2>/dev/null || ls -la /var/vmail/coneza.de/ai/Maildir/new/ 2>/dev/null

echo "=== POSTFIX LOGS FOR ai@coneza.de ==="
docker logs --since 3h mailcowdockerized-postfix-mailcow-1 2>&1 | grep -i 'ai@coneza.de' | tail -n 30
"""
    out, err, rc = run_remote_ssh(cmd)
    print("Email check:\n", out)
    if err:
        print("ERR:\n", err)

def test_delivery():
    cmd = """
docker exec mailcowdockerized-postfix-mailcow-1 sendmail -f test@coneza.de ai@coneza.de << 'EOF'
Subject: Test Delivery to AI
From: test@coneza.de
To: ai@coneza.de

Hello AI, this is a test delivery.
EOF
sleep 2
docker exec mailcowdockerized-dovecot-mailcow-1 doveadm search -u ai@coneza.de mailbox INBOX all
"""
    out, err, rc = run_remote_ssh(cmd)
    print("Delivery test:\n", out)
    if err:
        print("ERR:\n", err)

if __name__ == '__main__':
    test_delivery()




