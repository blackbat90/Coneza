import subprocess

remote_code = """
import subprocess

db_pw = subprocess.check_output("docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2", shell=True, text=True).strip()
cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", "SELECT * FROM tfa WHERE username='s.saleem@coneza.de';"]
out = subprocess.check_output(cmd, text=True)
print("TFA records:\n", out)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_check_tfa.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_check_tfa.py", "root@195.90.215.204:/tmp/check_tfa.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/check_tfa.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
