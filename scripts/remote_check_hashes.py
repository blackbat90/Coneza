import subprocess

def run_sql(q):
    pw = subprocess.check_output("docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2", shell=True, text=True).strip()
    cmd = ["docker", "exec", "-i", "mailcowdockerized-mysql-mailcow-1", "mysql", "-u", "mailcow", f"-p{pw}", "mailcow", "-N", "-e", q]
    return subprocess.check_output(cmd, text=True)

out = run_sql("SELECT username, password FROM mailbox UNION SELECT username, password FROM admin;")
candidates = [
    "conezaLoopHole",
    "conezaLoopHole!",
    "ConezaSecure2026!",
    "Coneza2026!",
    "Coneza123!",
    "admin",
    "coneza",
    "Coneza!",
    "coneza2026",
    "123456",
    "password"
]

for line in out.strip().split("\n"):
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) != 2:
        continue
    u, h = parts[0], parts[1]
    clean_h = h.replace("{BLF-CRYPT}", "")
    matched = False
    for c in candidates:
        # Use php inside php-fpm container to verify password
        php_code = f'echo password_verify("{c}", "{clean_h}") ? "yes" : "no";'
        cmd = ["docker", "exec", "mailcowdockerized-php-fpm-mailcow-1", "php", "-r", php_code]
        res = subprocess.check_output(cmd, text=True).strip()
        if res == "yes":
            print(f"MATCH for {u}: '{c}'")
            matched = True
            break
    if not matched:
        print(f"No match for {u}")
