import subprocess
out = subprocess.check_output("find / -name Dockerfile 2>/dev/null | grep -i coneza || true", shell=True, text=True)
print("Dockerfiles: " + repr(out))
out2 = subprocess.check_output("find /srv -maxdepth 3 2>/dev/null", shell=True, text=True)
print("In /srv: " + repr(out2))
