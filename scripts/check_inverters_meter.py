import subprocess
import sys

def check_backend():
    script_db = """cat << 'PYEOF' | docker exec -i coneza-backend-server python3
import sqlite3
con = sqlite3.connect('/data/coneza_backend.db')
con.row_factory = sqlite3.Row
cur = con.execute("SELECT device_id, name, status, controller_state, last_heartbeat FROM devices WHERE device_id IN ('siemens-pac-nap', 'solinteg-inv-01', 'solinteg-inv-02', 'byd-bess-01', 'grid-sim-enbw')")
for r in cur.fetchall():
    d = dict(r)
    print(f"[{d['status']}] {d['name']} ({d['device_id']})")
    print(f"      Zustand: {d['controller_state']} | Letzter Heartbeat: {d['last_heartbeat']}")
PYEOF
"""
    p = subprocess.Popen(['ssh', 'root@195.90.215.204', 'bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(input=script_db.replace('\r\n', '\n').encode('utf-8'))
    print("=== 1. STATUS IM CLOUD-PORTAL (coneza.de) ===")
    sys.stdout.buffer.write(out)
    if err:
        sys.stderr.buffer.write(err)

def check_live_modbus():
    script_ipc = """cat << 'PYEOF' | python3
import socket, struct

def read_float(port, reg, count=2):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        s.connect(('127.0.0.1', port))
        req = struct.pack('>HHHBBHH', 1, 0, 6, 1, 3, reg, count)
        s.sendall(req)
        resp = s.recv(1024)
        s.close()
        if len(resp) >= 9 + count*2:
            raw = resp[9:9+4]
            return round(struct.unpack('>f', raw)[0], 2)
        return 'Err_len'
    except Exception as e:
        return f'Err: {e}'

print(f"E-Meter (Siemens SENTRON PAC3200 @ Port 5020): {read_float(5020, 24)} kW Wirkleistung, {read_float(5020, 6)} V, {read_float(5020, 54)} Hz")
print(f"WR 1    (Solinteg MHT-75K #1     @ Port 5021): {read_float(5021, 0)} kW Wirkleistung (Nenn: {read_float(5021, 8)} kW)")
print(f"WR 2    (Solinteg MHT-75K #2     @ Port 5022): {read_float(5022, 0)} kW Wirkleistung (Nenn: {read_float(5022, 8)} kW)")
print(f"BESS    (BYD Battery-Box         @ Port 5023): {read_float(5023, 0)} kW Ladeleistung, SoC: {read_float(5023, 2)} %")
PYEOF
"""
    p = subprocess.Popen(['ssh', 'root@192.168.8.186', 'bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(input=script_ipc.replace('\r\n', '\n').encode('utf-8'))
    print("\n=== 2. LIVE MODBUS-TCP REGISTER-ABFRAGE (IPC 192.168.8.186) ===")
    sys.stdout.buffer.write(out)
    if err:
        sys.stderr.buffer.write(err)

if __name__ == '__main__':
    check_backend()
    check_live_modbus()
