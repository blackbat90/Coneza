import subprocess

remote_code = """
import subprocess
out = subprocess.check_output("grep -n -A 25 'function verify_hash(' /srv/mail-coneza/mailcow/data/web/inc/functions.inc.php", shell=True, text=True)
print(out)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_test_auth.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_test_auth.py", "root@195.90.215.204:/tmp/test_auth.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/test_auth.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
