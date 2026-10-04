
import subprocess

for cmd in [
    "docker ps --format '{{.Names}}'",
    "systemctl is-active coneza-backend 2>/dev/null || true",
    "ls -la /srv/coneza-portal 2>/dev/null || ls -la /srv/Coneza* 2>/dev/null || true",
]:
    out = subprocess.check_output(cmd, shell=True, text=True)
    print("=== " + cmd + " ===")
    print(out)
