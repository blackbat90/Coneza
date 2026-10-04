
import subprocess
print("=== PHP-FPM logs ===")
print(subprocess.check_output("docker logs --tail 20 mailcowdockerized-php-fpm-mailcow-1", shell=True, text=True))
print("=== Dovecot logs ===")
print(subprocess.check_output("docker logs --tail 20 mailcowdockerized-dovecot-mailcow-1", shell=True, text=True))
