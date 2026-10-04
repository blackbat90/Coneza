"""
Deploy Plant Devices Simulation (Siemens PAC, 2x Solinteg, BYD BESS) to IPC 192.168.8.186
"""
import subprocess
import time
import sys

IPC_HOST = "root@192.168.8.186"
REMOTE_DIR = "/opt/coneza-edge"

def run_cmd(cmd):
    print(f"RUN: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed code {res.returncode}: {cmd}")
    return res

def main():
    print("=== Step 1: Copy plant_devices_sim.py and driver files ===")
    run_cmd(f'ssh {IPC_HOST} "mkdir -p {REMOTE_DIR}/edge/drivers/meters {REMOTE_DIR}/edge/drivers/inverters"')
    run_cmd(f'scp edge/plant_devices_sim.py {IPC_HOST}:{REMOTE_DIR}/edge/plant_devices_sim.py')
    run_cmd(f'scp edge/drivers/meters/siemens.py {IPC_HOST}:{REMOTE_DIR}/edge/drivers/meters/siemens.py')
    run_cmd(f'scp edge/drivers/registry.py {IPC_HOST}:{REMOTE_DIR}/edge/drivers/registry.py')

    print("=== Step 2: Install systemd service coneza-plant-devices.service ===")
    service_content = """[Unit]
Description=Coneza Plant Devices Simulator & Telemetry Sync (Siemens PAC, 2x Solinteg, BYD BESS)
After=network-online.target coneza-portal-tunnel.service
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/coneza-edge
Environment="PYTHONPATH=/opt/coneza-edge"
Environment="CONEZA_BACKEND_URL=https://coneza.de/portal"
Environment="PLANT_ID=plant-enbw-hybrid-01"
ExecStart=/usr/bin/python3 -m edge.plant_devices_sim
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    service_file = "scripts/coneza-plant-devices.service"
    with open(service_file, "w", encoding="utf-8") as f:
        f.write(service_content)

    run_cmd(f'scp {service_file} {IPC_HOST}:/etc/systemd/system/coneza-plant-devices.service')
    run_cmd(f'ssh {IPC_HOST} "systemctl daemon-reload && systemctl enable coneza-plant-devices.service && systemctl restart coneza-plant-devices.service"')

    print("=== Step 3: Check service status and logs ===")
    time.sleep(2)
    run_cmd(f'ssh {IPC_HOST} "systemctl status coneza-plant-devices.service --no-pager"')
    run_cmd(f'ssh {IPC_HOST} "journalctl -u coneza-plant-devices.service --no-pager -n 25"')

if __name__ == "__main__":
    main()
