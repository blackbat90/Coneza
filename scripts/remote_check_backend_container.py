import subprocess
out = subprocess.check_output("docker inspect coneza-backend-server --format '{{json .Mounts}}'", shell=True, text=True)
print("Mounts: " + out)
out2 = subprocess.check_output("docker inspect coneza-backend-server --format '{{.Config.WorkingDir}} {{.Config.Image}}'", shell=True, text=True)
print("Config: " + out2)
