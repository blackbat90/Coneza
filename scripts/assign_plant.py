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
plant_id = 'plant-enbw-hybrid-01'
cur.execute('''
    UPDATE devices SET plant_id = ? WHERE device_id IN (
        'coneza-phoenix-axcf2152',
        'siemens-pac-nap',
        'solinteg-inv-01',
        'solinteg-inv-02',
        'byd-bess-01'
    )
''', (plant_id,))
conn.commit()

cur.execute('SELECT device_id, plant_id, name, status, last_heartbeat FROM devices WHERE plant_id = ?', (plant_id,))
rows = [dict(r) for r in cur.fetchall()]
print('ENBW PLANT DEVICES:')
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
