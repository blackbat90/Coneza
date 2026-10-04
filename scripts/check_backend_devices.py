import subprocess
import sys

script = """cat << 'PYEOF' | docker exec -i coneza-backend-server python3
import sqlite3
con = sqlite3.connect('/data/coneza_backend.db')
con.row_factory = sqlite3.Row
print('--- PLANTS ---')
for r in con.execute("SELECT id, name, status, grid_operator FROM plants").fetchall():
    print(dict(r))
print('--- DEVICES ---')
for r in con.execute("SELECT device_id, name, status, controller_state, plant_id, last_heartbeat FROM devices").fetchall():
    print(dict(r))
PYEOF
"""

p = subprocess.Popen(
    ['ssh', 'root@195.90.215.204', 'bash'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
out, err = p.communicate(input=script.replace('\r\n', '\n').encode('utf-8'))
sys.stdout.buffer.write(out)
if err:
    sys.stderr.buffer.write(err)
