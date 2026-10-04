
import subprocess

php_test = """
ini_set('display_errors', '1');
error_reporting(E_ALL);
$_SERVER['DOCUMENT_ROOT'] = '/web';
require_once '/web/inc/prerequisites.inc.php';
$res = user_login('s.saleem@coneza.de', 'ConezaSecure2026!', array('is_internal' => true, 'service' => 'NONE'));
echo "USER_LOGIN RESULT: " . var_export($res, true) . PHP_EOL;
"""

cmd = ["docker", "exec", "mailcowdockerized-php-fpm-mailcow-1", "php", "-r", php_test]
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
