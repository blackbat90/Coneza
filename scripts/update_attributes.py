import subprocess

remote_code = """import subprocess

db_pw = subprocess.check_output("docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2", shell=True, text=True).strip()
cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", "UPDATE mailbox SET attributes = JSON_SET(attributes, '$.force_tfa', '0', '$.force_pw_update', '0') WHERE username='s.saleem@coneza.de';"]
subprocess.run(cmd, check=True)

# Flush Redis
subprocess.run("docker exec mailcowdockerized-redis-mailcow-1 redis-cli -a mailcow FLUSHALL", shell=True, check=True)

# Verify
cmd2 = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", "SELECT username, attributes FROM mailbox WHERE username='s.saleem@coneza.de';"]
out = subprocess.check_output(cmd2, text=True)
print("Updated attributes: " + out)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_update_attr.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_update_attr.py", "root@195.90.215.204:/tmp/update_attr.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/update_attr.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
