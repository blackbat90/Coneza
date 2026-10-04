from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import create_access_token

client = TestClient(app)
token = create_access_token(1, "admin", "SUPER_ADMIN")
headers = {"Authorization": f"Bearer {token}"}

print("Running 1-Click Auto-Configure with SLD + E9...")
res = client.post(
    "/api/plants/auto-configure",
    data={
        "use_sample_sld": "true",
        "use_sample_grid_doc": "true",
        "grid_doc_type": "E9",
        "target_device_id": "coneza-phoenix-axcf2152"
    },
    headers=headers
)
print("Auto-Configure Status:", res.status_code)
data = res.json()
print("Plant Name:", data.get("plant", {}).get("name"))
print("Target PCU:", data.get("device_id"))
registers = data.get("modbus_holding_registers", [])
print(f"Total Modbus Holding Registers: {len(registers)}")

if registers:
    print(f"Sample Register [40001]: {registers[0]['name']} = {registers[0]['value']} ({registers[0]['vde_reference']})")
    qu_regs = [r for r in registers if "QU" in r.get("name", "")]
    print(f"Q(U) Statik Registers count: {len(qu_regs)}")

# Test Direct Deploy
config_id = data.get("configuration_id")
plant_id = data.get("plant", {}).get("id")
print(f"\nDeploying Config {config_id} directly to PCU...")
deploy_res = client.post(
    "/api/pcu/direct-deploy",
    json={
        "configuration_id": config_id,
        "device_id": "coneza-phoenix-axcf2152",
        "plant_id": plant_id
    },
    headers=headers
)
print("Direct Deploy Status:", deploy_res.status_code)
print("Deploy Response:", deploy_res.json())
