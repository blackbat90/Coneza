import subprocess

db_pw = subprocess.check_output("docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2", shell=True, text=True).strip()
cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", "UPDATE mailbox SET attributes = JSON_SET(attributes, '$.force_tfa', '0', '$.force_pw_update', '0') WHERE username='s.saleem@coneza.de';"]
subprocess.run(cmd, check=True)

# Flush Redis
subprocess.run("docker exec mailcowdockerized-redis-mailcow-1 redis-cli -a mailcow FLUSHALL", shell=True, check=True)

# Verify
cmd2 = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", "SELECT username, attributes FROM mailbox WHERE username='s.saleem@coneza.de';"]
out = subprocess.check_output(cmd2, text=True)
print("Updated attributes: " + out)
