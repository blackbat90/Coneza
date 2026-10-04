
import subprocess

db_pw = subprocess.check_output("docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2", shell=True, text=True).strip()
cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", "SELECT * FROM tfa WHERE username='s.saleem@coneza.de';"]
out = subprocess.check_output(cmd, text=True)
print("TFA records:
", out)
