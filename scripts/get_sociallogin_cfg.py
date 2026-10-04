import subprocess

cmd = ["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "docker exec -u www-data nextcloud php occ config:app:get sociallogin custom_providers"]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
