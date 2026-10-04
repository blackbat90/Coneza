import subprocess

remote_code = """import subprocess
out = subprocess.check_output("find / -name Dockerfile 2>/dev/null | grep -i coneza || true", shell=True, text=True)
print("Dockerfiles: " + repr(out))
out2 = subprocess.check_output("find /srv -maxdepth 3 2>/dev/null", shell=True, text=True)
print("In /srv: " + repr(out2))
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_find_repo.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_find_repo.py", "root@195.90.215.204:/tmp/find_repo.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/find_repo.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
