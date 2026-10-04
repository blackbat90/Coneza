
import subprocess
out = subprocess.check_output("grep -n -A 25 'function verify_hash(' /srv/mail-coneza/mailcow/data/web/inc/functions.inc.php", shell=True, text=True)
print(out)
