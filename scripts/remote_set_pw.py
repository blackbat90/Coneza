
import subprocess

new_pw = "ConezaSecure2026!"
user = "s.saleem@coneza.de"

# 1. Generate hash via PHP inside php-fpm container
php_cmd = f'echo "{new_pw}";'
hash_cmd = ["docker", "exec", "mailcowdockerized-php-fpm-mailcow-1", "php", "-r", f'echo "{{BLF-CRYPT}}" . password_hash("{new_pw}", PASSWORD_BCRYPT);']
hash_res = subprocess.check_output(hash_cmd, text=True).strip()
print("Generated PHP bcrypt hash:", hash_res)

# 2. Get MySQL password
db_pw = subprocess.check_output(
    "docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2",
    shell=True, text=True
).strip()

# 3. Update mailbox table
sql = f"UPDATE mailbox SET password = '{hash_res}' WHERE username = '{user}';"
cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{db_pw}", "mailcow", "-e", sql]
subprocess.run(cmd, check=True)
print("Updated database for", user)

# 4. Verify authentication using doveadm auth test
auth_cmd = ["docker", "exec", "mailcowdockerized-dovecot-mailcow-1", "doveadm", "auth", "test", user, new_pw]
auth_res = subprocess.run(auth_cmd, capture_output=True, text=True)
print("Auth test returncode:", auth_res.returncode)
print("Auth test stdout:", auth_res.stdout)
print("Auth test stderr:", auth_res.stderr)
