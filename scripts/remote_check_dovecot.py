
import subprocess
out = subprocess.check_output("docker exec mailcowdockerized-php-fpm-mailcow-1 cat /mailcowauth/mailcowauth.php", shell=True, text=True)
print(out)
