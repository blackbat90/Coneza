import subprocess

remote_py = """
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
    "coneza"
]

import crypt
for line in out.strip().split('\\n'):
    if not line: continue
    parts = line.split('\\t')
    if len(parts) != 2: continue
    u, h = parts[0], parts[1]
    clean_h = h.replace("{BLF-CRYPT}", "")
    matched = False
    for c in candidates:
        try:
            if crypt.crypt(c, clean_h) == clean_h:
                print(f"MATCH for {u}: {c}")
                matched = True
                break
        except Exception as e:
            pass
    if not matched:
        print(f"No match for {u}")
"""

res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 -c " + repr(remote_py)], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
