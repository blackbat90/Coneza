import subprocess

cmd = ["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "docker exec mailcowdockerized-php-fpm-mailcow-1 ls -la /web/oauth/profile.php"]
res = subprocess.run(cmd, capture_output=True, text=True)
print("PHP-FPM container:\n", res.stdout, res.stderr)
