import subprocess

remote_code = """
import subprocess

php_test = \"\"\"
ini_set('display_errors', '1');
error_reporting(E_ALL);
$_SERVER['DOCUMENT_ROOT'] = '/web';
require_once '/web/inc/prerequisites.inc.php';
$res = user_login('s.saleem@coneza.de', 'ConezaSecure2026!', array('is_internal' => true, 'service' => 'NONE'));
echo "USER_LOGIN RESULT: " . var_export($res, true) . PHP_EOL;
\"\"\"

cmd = ["docker", "exec", "mailcowdockerized-php-fpm-mailcow-1", "php", "-r", php_test]
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_test_login.py", "w") as f:
    f.write(remote_code)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_test_login.py", "root@195.90.215.204:/tmp/test_login.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/test_login.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
