import subprocess

cmd = ["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "cat /srv/mail-coneza/mailcow/data/web/oauth/profile.php"]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
