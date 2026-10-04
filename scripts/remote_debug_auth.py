
import subprocess

php_test = """
$_SERVER['DOCUMENT_ROOT'] = '/web';
require_once '/web/inc/vars.inc.php';
require_once '/web/inc/lib/vendor/autoload.php';
$redis = new Redis();
$redis->connect('redis-mailcow', 6379);
$redis->auth(getenv('REDISPASS'));
$pdo = new PDO($database_type . ":unix_socket=" . $database_sock . ";dbname=" . $database_name, $database_user, $database_pass);

require_once '/web/inc/functions.inc.php';
require_once '/web/inc/functions.auth.inc.php';
require_once '/web/inc/sessions.inc.php';
require_once '/web/inc/functions.mailbox.inc.php';

$user = 's.saleem@coneza.de';
$authenticators = get_tfa($user);
echo "6. authenticators: " . json_encode($authenticators) . PHP_EOL;

$row['attributes'] = json_decode('{"force_pw_update": "0", "force_tfa": "0", "tls_enforce_in": "1", "tls_enforce_out": "1", "sogo_access": "1", "imap_access": "1", "pop3_access": "1", "smtp_access": "1", "sieve_access": "1", "eas_access": "1", "dav_access": "1", "relayhost": "0", "passwd_update": "2026-09-27 12:02:13", "mailbox_format": "maildir:", "quarantine_notification": "weekly", "quarantine_category": "reject", "attribute_hash": "", "recovery_email": null}', true);

if (!isset($authenticators['additional']) || !is_array($authenticators['additional']) || count($authenticators['additional']) == 0) {
    echo "7. Inside no authenticators branch!" . PHP_EOL;
}
"""

cmd = ["docker", "exec", "mailcowdockerized-php-fpm-mailcow-1", "php", "-r", php_test]
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
