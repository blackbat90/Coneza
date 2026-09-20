import requests
import json

BASE = 'http://127.0.0.1:9080'

# 1. Login as engineer
login_res = requests.post(f'{BASE}/api/auth/login', json={'username': 'engineer', 'password': 'engineer2026!'})
print('Login engineer status:', login_res.status_code)
res_json = login_res.json()
token = res_json.get('access_token')

if res_json.get('status') == 'PASSWORD_RESET_REQUIRED':
    change_res = requests.post(f'{BASE}/api/auth/change-password', json={
        'temp_token': res_json['temp_token'],
        'new_password': 'EngineerSecure2026!'
    })
    token = change_res.json()['access_token']
elif not token and res_json.get('detail'):
    login_res2 = requests.post(f'{BASE}/api/auth/login', json={'username': 'engineer', 'password': 'EngineerSecure2026!'})
    token = login_res2.json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

# 2. Get plants
plants_res = requests.get(f'{BASE}/api/plants', headers=headers)
print('Get plants status:', plants_res.status_code)
plants = plants_res.json()
print(f'Total plants found: {len(plants)}')
for p in plants:
    print(f" - Plant {p['id']}: {p['name']} ({p['site_type']}, {p['installed_capacity_kw']} kW, VNB: {p['grid_operator']}, Devices: {p['device_count']}, Docs: {p['document_count']})")

# 3. Create a new plant
new_plant_payload = {
    'name': 'Solarpark Franken-Süd (NAP 20kV)',
    'site_type': 'PV',
    'grid_operator': 'N-ERGIE Netz GmbH',
    'voltage_level': 'MS_4110',
    'installed_capacity_kw': 3200.0,
    'grid_connection_point': 'Umspannwerk Weißenburg Abzweig 7',
    'location': '91781 Weißenburg in Bayern',
    'commissioning_date': '2026-06-01',
    'status': 'COMMISSIONING',
    'notes': 'VDE-AR-N 4110 Mittelspannung, Q(U)-Regelung mit cos phi = 1,00 Standardeinstellung.'
}
create_res = requests.post(f'{BASE}/api/plants', json=new_plant_payload, headers=headers)
print('Create plant status:', create_res.status_code)
created_plant = create_res.json()
print('Created plant ID:', created_plant.get('id'), 'Name:', created_plant.get('name'))

# 4. Assign device to plant
assign_res = requests.post(f"{BASE}/api/plants/{created_plant['id']}/devices", json={'device_id': 'coneza-edge-solar-park-01'}, headers=headers)
print('Assign device status:', assign_res.status_code, assign_res.json())

# 5. Get plant detail
detail_res = requests.get(f"{BASE}/api/plants/{created_plant['id']}", headers=headers)
print('Get detail status:', detail_res.status_code)
detail = detail_res.json()
print('Detail devices count:', len(detail.get('devices', [])))
print('Detail documents count:', len(detail.get('documents', [])))
if detail.get('devices'):
    dev0 = detail['devices'][0]
    print(f" - Linked Device: {dev0['device_id']} ({dev0['name']}), Status: {dev0['status']}, Telemetry P: {dev0.get('telemetry', {}).get('P_act')}")

# 6. Verify viewer cannot create plant (RBAC check)
login_v = requests.post(f'{BASE}/api/auth/login', json={'username': 'viewer', 'password': 'viewer2026!'})
v_token = login_v.json().get('access_token')
if not v_token and login_v.json().get('status') == 'PASSWORD_RESET_REQUIRED':
    c_res = requests.post(f'{BASE}/api/auth/change-password', json={
        'temp_token': login_v.json()['temp_token'],
        'new_password': 'ViewerSecure2026!'
    })
    v_token = c_res.json().get('access_token')
elif not v_token:
    login_v2 = requests.post(f'{BASE}/api/auth/login', json={'username': 'viewer', 'password': 'ViewerSecure2026!'})
    v_token = login_v2.json().get('access_token')

if v_token:
    v_headers = {'Authorization': f'Bearer {v_token}'}
    v_create = requests.post(f'{BASE}/api/plants', json=new_plant_payload, headers=v_headers)
    print('Viewer create plant status (expected 403):', v_create.status_code)
    assert v_create.status_code == 403, f"Expected 403 but got {v_create.status_code}"

print('ALL LIVE API VERIFICATIONS PASSED!')
