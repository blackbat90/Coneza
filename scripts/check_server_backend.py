import subprocess

remote_code = """import subprocess
out = subprocess.check_output("docker inspect coneza-backend-server --format '{{json .Mounts}}'", shell=True, text=True)
print("Mounts: " + out)
out2 = subprocess.check_output("docker inspect coneza-backend-server --format '{{.Config.WorkingDir}} {{.Config.Image}}'", shell=True, text=True)
print("Config: " + out2)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_check_backend_container.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_check_backend_container.py", "root@195.90.215.204:/tmp/check_bc.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/check_bc.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
