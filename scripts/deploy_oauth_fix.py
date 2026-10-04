import subprocess
import json

new_profile_php = """<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/inc/prerequisites.inc.php';

if (!$oauth2_server->verifyResourceRequest(OAuth2\Request::createFromGlobals())) {
  $oauth2_server->getResponse()->send();
  die;
}
$token = $oauth2_server->getAccessTokenData(OAuth2\Request::createFromGlobals());
$stmt = $pdo->prepare("SELECT * FROM `mailbox` WHERE `username` = :username AND `active` = '1'");
$stmt->execute(array(':username' => $token['user_id']));
$mailbox = $stmt->fetch(PDO::FETCH_ASSOC);

$displayName = !empty($mailbox['name']) ? $mailbox['name'] : $token['user_id'];
$email = !empty($mailbox['username']) ? $mailbox['username'] : $token['user_id'];

header('Content-Type: application/json');
echo json_encode(array(
  'success' => true,
  'username' => $token['user_id'],
  'id' => $token['user_id'],
  'identifier' => $token['user_id'],
  'email' => $email,
  'full_name' => $displayName,
  'displayName' => $displayName,
  'name' => $displayName,
  'created' => (!empty($mailbox['created']) ? $mailbox['created'] : ''),
  'modified' => (!empty($mailbox['modified']) ? $mailbox['modified'] : ''),
  'active' => (!empty($mailbox['active']) ? $mailbox['active'] : '1'),
));
exit;
"""

with open("c:/Workplace/Coneza/Coneza/scripts/profile.php", "w") as f:
    f.write(new_profile_php)

print("1. Uploading profile.php to server...")
subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/profile.php", "root@195.90.215.204:/tmp/profile.php"], check=True)

remote_bash = """
# Backup original if not already backed up
if [ ! -f /srv/mail-coneza/mailcow/data/web/oauth/profile.php.bak ]; then
    cp /srv/mail-coneza/mailcow/data/web/oauth/profile.php /srv/mail-coneza/mailcow/data/web/oauth/profile.php.bak
fi

# Copy new file
cp /tmp/profile.php /srv/mail-coneza/mailcow/data/web/oauth/profile.php
chmod 644 /srv/mail-coneza/mailcow/data/web/oauth/profile.php

# Test php lint
docker exec mailcowdockerized-php-fpm-mailcow-1 php -l /web/oauth/profile.php

# Update Nextcloud sociallogin configuration: scope to profile
CONFIG='{"custom_oauth2": [{"name": "mailcow", "title": "Coneza SSO (Mail-Konto)", "authorizeUrl": "https://mail.coneza.de/oauth/authorize", "tokenUrl": "https://mail.coneza.de/oauth/token", "profileUrl": "https://mail.coneza.de/oauth/profile", "clientId": "nextcloud-cloudshare", "clientSecret": "ConezaCloudSSO2026!", "scope": "profile", "groups": ["admin"], "auto_create_user": true, "update_profile_on_login": true, "style": "mailcow"}]}'

docker exec -u www-data nextcloud php occ config:app:set sociallogin custom_providers --value="$CONFIG"

echo "=== Updated sociallogin config ==="
docker exec -u www-data nextcloud php occ config:app:get sociallogin custom_providers
"""

print("2. Applying fix on remote server...")
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", remote_bash], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
