import subprocess

remote_code = """import subprocess
out = subprocess.check_output("cat /srv/coneza-backend/scripts/deploy_docker_backend.sh", shell=True, text=True)
print("deploy_docker_backend.sh: " + repr(out))
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_view_deploy.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_view_deploy.py", "root@195.90.215.204:/tmp/view_dep.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/view_dep.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
