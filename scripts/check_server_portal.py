import subprocess

remote_code = """
import subprocess

for cmd in [
    "docker ps --format '{{.Names}}'",
    "systemctl is-active coneza-backend 2>/dev/null || true",
    "ls -la /srv/coneza-portal 2>/dev/null || ls -la /srv/Coneza* 2>/dev/null || true",
]:
    out = subprocess.check_output(cmd, shell=True, text=True)
    print("=== " + cmd + " ===")
    print(out)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_check_portal.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_check_portal.py", "root@195.90.215.204:/tmp/check_portal.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/check_portal.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
