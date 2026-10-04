
import subprocess
out = subprocess.check_output("sed -n '145,170p' /srv/mail-coneza/mailcow/data/web/inc/functions.inc.php", shell=True, text=True)
print(out)
