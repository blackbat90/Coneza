"""
Deploy Physical Phoenix Contact Gateway to IPC 192.168.8.186
"""
import os
import subprocess
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
        raise RuntimeError(f"Command failed with code {res.returncode}: {cmd}")
    return res

def main():
    print("=== Step 1: Create directories on IPC ===")
    run_cmd(f'ssh {IPC_HOST} "mkdir -p {REMOTE_DIR}/edge/phoenix_eza"')

    print("=== Step 2: Copy updated edge files to IPC ===")
    files_to_copy = [
        ("edge/backend_client.py", f"{REMOTE_DIR}/edge/backend_client.py"),
        ("edge/physical_gateway.py", f"{REMOTE_DIR}/edge/physical_gateway.py"),
        ("edge/phoenix_eza/register_map.py", f"{REMOTE_DIR}/edge/phoenix_eza/register_map.py"),
        ("edge/phoenix_eza/controller.py", f"{REMOTE_DIR}/edge/phoenix_eza/controller.py"),
    ]

    for local_f, remote_f in files_to_copy:
        run_cmd(f'scp {local_f} {IPC_HOST}:{remote_f}')

    # Create __init__.py files
    run_cmd(f'ssh {IPC_HOST} "touch {REMOTE_DIR}/edge/__init__.py {REMOTE_DIR}/edge/phoenix_eza/__init__.py"')

    print("=== Step 3: Stop old virtual simulator container ===")
    run_cmd(f'ssh {IPC_HOST} "docker stop coneza-simulator-eza-simulator-1 2>/dev/null || true"')

    print("=== Step 4: Install systemd service for physical Phoenix gateway ===")
    service_content = """[Unit]
Description=Coneza Physical Phoenix Contact EZA Controller Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/coneza-edge
Environment="PYTHONPATH=/opt/coneza-edge"
Environment="CONEZA_BACKEND_URL=https://coneza.de/portal"
Environment="DEVICE_ID=coneza-phoenix-axcf2152"
Environment="DEVICE_NAME=Phoenix Contact AXC F 2152 (EZA-Regler)"
Environment="EZA_CONTROLLER_HOST=192.168.1.10"
Environment="EZA_CONTROLLER_PORT=502"
Environment="PLANT_ID=plant-solar-west-01"
ExecStart=/usr/bin/python3 -m edge.physical_gateway
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    service_local_path = "scripts/coneza-phoenix-gateway.service"
    with open(service_local_path, "w", encoding="utf-8") as f:
        f.write(service_content)

    run_cmd(f'scp {service_local_path} {IPC_HOST}:/etc/systemd/system/coneza-phoenix-gateway.service')
    run_cmd(f'ssh {IPC_HOST} "systemctl daemon-reload && systemctl enable coneza-phoenix-gateway.service && systemctl restart coneza-phoenix-gateway.service"')

    print("=== Step 5: Check service status and initial logs ===")
    import time
    time.sleep(2)
    run_cmd(f'ssh {IPC_HOST} "systemctl status coneza-phoenix-gateway.service --no-pager"')
    run_cmd(f'ssh {IPC_HOST} "journalctl -u coneza-phoenix-gateway.service --no-pager -n 25"')

if __name__ == "__main__":
    main()
