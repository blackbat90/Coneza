import subprocess

candidates = [
    "conezaLoopHole",
    "ConezaSecure2026!",
    "conezaLoopHole!",
    "Coneza2026!",
    "Coneza123!",
    "admin",
    "coneza",
    "Coneza!",
]

users = ["s.saleem@coneza.de", "w.ahmad@coneza.de"]

for u in users:
    print(f"Testing user {u}...")
    for p in candidates:
        cmd = f"docker exec mailcowdockerized-dovecot-mailcow-1 doveadm auth test {u} '{p}'"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  FOUND PASSWORD for {u}: {p}")
            break
        else:
            # print(f"  Failed for {p}: {res.stderr.strip()}")
            pass
    else:
        print(f"  None of common candidate passwords matched for {u}")
