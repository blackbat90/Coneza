import subprocess

remote_code = """
import subprocess
print("=== PHP-FPM logs ===")
print(subprocess.check_output("docker logs --tail 20 mailcowdockerized-php-fpm-mailcow-1", shell=True, text=True))
print("=== Dovecot logs ===")
print(subprocess.check_output("docker logs --tail 20 mailcowdockerized-dovecot-mailcow-1", shell=True, text=True))
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_check_logs.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_check_logs.py", "root@195.90.215.204:/tmp/check_logs.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/check_logs.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
