import subprocess

def main():
    p = subprocess.Popen(
        ['ssh', 'root@195.90.215.204', 'bash -s'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    cmd = """
docker exec coneza-backend-server python -c "
import json
from backend.database import get_connection
conn = get_connection()
cur = conn.cursor()
cur.execute('SELECT device_id, plant_id, name, status, last_heartbeat FROM devices')
rows = [dict(r) for r in cur.fetchall()]
print('ALL DEVICES IN DB:')
print(json.dumps(rows, indent=2))
"
"""
    clean = cmd.replace('\r\n', '\n').strip() + '\n'
    out, err = p.communicate(input=clean)
    print("OUTPUT:\n", out)
    if err:
        print("ERR:\n", err)

if __name__ == '__main__':
    main()
