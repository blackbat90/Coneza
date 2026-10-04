"""
Create/Configure EnBW Hybrid Plant and assign devices in Coneza Portal DB
"""
import subprocess
import sys

def main():
    p = subprocess.Popen(
        ['ssh', 'root@195.90.215.204', 'bash -s'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    cmd = """
docker exec coneza-backend-server python -c "
import json
from datetime import datetime
from backend.database import get_connection

conn = get_connection()
cur = conn.cursor()

# 1. Create or update EnBW Plant
plant_id = 'plant-enbw-hybrid-01'
cur.execute('SELECT id FROM plants WHERE id = ?', (plant_id,))
row = cur.fetchone()

if not row:
    cur.execute('''
        INSERT INTO plants (
            id, name, site_type, grid_operator, voltage_level,
            installed_capacity_kw, grid_connection_point, location, commissioning_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        plant_id,
        'Solar & BESS Park EnBW (NAP 20kV)',
        'HYBRID',
        'Netze BW GmbH (EnBW)',
        'MS_4110',
        300.0,
        'Umspannwerk EnBW / Übergabestation 20kV',
        'Baden-Württemberg, Deutschland',
        datetime.utcnow().strftime('%Y-%m-%d')
    ))
    print(f'Created plant {plant_id}')
else:
    cur.execute('''
        UPDATE plants SET
            name = 'Solar & BESS Park EnBW (NAP 20kV)',
            site_type = 'HYBRID',
            grid_operator = 'Netze BW GmbH (EnBW)',
            voltage_level = 'MS_4110',
            installed_capacity_kw = 300.0,
            grid_connection_point = 'Umspannwerk EnBW / Übergabestation 20kV'
        WHERE id = ?
    ''', (plant_id,))
    print(f'Updated plant {plant_id}')

# 2. Assign Phoenix SPS to EnBW plant
cur.execute('UPDATE devices SET plant_id = ? WHERE device_id = ?', (plant_id, 'coneza-phoenix-axcf2152'))

conn.commit()

# 3. Print plants and devices
cur.execute('SELECT id, name, site_type, grid_operator, installed_capacity_kw FROM plants WHERE id = ?', (plant_id,))
print('PLANT INFO:', [dict(r) for r in cur.fetchall()])

cur.execute('SELECT device_id, plant_id, name, status, controller_host FROM devices')
print('ALL DEVICES:', [dict(r) for r in cur.fetchall()])
"
"""
    clean = cmd.replace('\r\n', '\n').strip() + '\n'
    out, err = p.communicate(input=clean)
    print("OUTPUT:\n", out)
    if err:
        print("ERR:\n", err)

if __name__ == '__main__':
    main()
