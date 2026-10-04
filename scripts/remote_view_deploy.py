import subprocess
out = subprocess.check_output("cat /srv/coneza-backend/scripts/deploy_docker_backend.sh", shell=True, text=True)
print("deploy_docker_backend.sh: " + repr(out))
