import subprocess

remote_code = """
import subprocess

db_pw = subprocess.check_output("docker exec mailcowdockerized-mysql-mailcow-1 env | grep MYSQL_PASSWORD | cut -d= -f2", shell=True, text=True).strip()

php_test = f\"\"\"
$pdo = new PDO('mysql:host=mysql-mailcow;dbname=mailcow', 'mailcow', '{db_pw}');
$stmt = $pdo->query("SELECT password FROM mailbox WHERE username='s.saleem@coneza.de'");
$db_hash = $stmt->fetchColumn();
echo "DB HASH: " . $db_hash . PHP_EOL;

require_once '/web/inc/functions.inc.php';
$check = verify_hash($db_hash, 'ConezaSecure2026!');
echo "VERIFY_HASH: " . var_export($check, true) . PHP_EOL;

$pw_check = password_verify('ConezaSecure2026!', substr($db_hash, 11));
echo "PASSWORD_VERIFY: " . var_export($pw_check, true) . PHP_EOL;
\"\"\"

cmd = ["docker", "exec", "mailcowdockerized-php-fpm-mailcow-1", "php", "-r", php_test]
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_test_verify.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_test_verify.py", "root@195.90.215.204:/tmp/test_v.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/test_v.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
