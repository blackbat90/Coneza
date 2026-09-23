"""Read-only local dashboard for the isolated software simulator."""
import asyncio
import json
import os
from datetime import datetime, timezone

PAGE = """<!doctype html><html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Coneza · Lokaler Simulator</title>
<style>body{margin:0;background:#101a28;color:#edf4ff;font:16px system-ui}main{max-width:1050px;margin:auto;padding:32px 24px}header{display:flex;justify-content:space-between;align-items:center;gap:20px}a{color:#83e4c2}h1{font-size:32px;margin-bottom:8px}.muted{color:#a9bad0}.badge{color:#ffd18a;border:1px solid #886333;padding:8px 14px;border-radius:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px;margin:24px 0}.card,details{background:#1b293c;border:1px solid #32445d;border-radius:16px;padding:20px}.value{font-size:30px;font-weight:650;margin-top:12px}table{width:100%;border-collapse:collapse}td{padding:10px 0;border-bottom:1px solid #32445d;overflow-wrap:anywhere}td:last-child{text-align:right}summary{cursor:pointer;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere}#error{color:#ffb6a9;min-height:24px}</style>
<main><header><strong>CONEZA / EDGE</strong><span class="badge">SIMULATION</span></header>
<h1>Dein lokaler EZA-Simulator</h1><p class="muted">Synthetische Messwerte · Keine Verbindung zur physischen PLC · Keine zertifizierte PCU</p>
<p id="identity"></p><p id="error" role="status">Verbindung wird aufgebaut …</p>
<div class="grid"><div class="card">Portal<div class="value" id="portal">—</div></div><div class="card">Wirkleistung<div class="value" id="power">—</div></div><div class="card">Blindleistung<div class="value" id="reactive">—</div></div><div class="card">Frequenz<div class="value" id="frequency">—</div></div></div>
<section class="card"><h2>Betriebswerte</h2><table><tbody id="measurements"></tbody></table><p class="muted" id="updated"></p></section>
<details style="margin-top:20px"><summary>Aktuelle Simulationseinstellungen ansehen</summary><pre id="configuration"></pre></details>
<p>Diese lokale Ansicht ist schreibgeschützt. Konfigurationen verwaltest du im <a href="https://coneza.de/portal/" target="_blank" rel="noopener">Coneza-Portal ↗</a>.</p>
<script>
const el=id=>document.getElementById(id);
async function refresh(){try{const r=await fetch('/api/status',{cache:'no-store',signal:AbortSignal.timeout(6000)});if(!r.ok)throw Error();const d=await r.json();el('identity').textContent=d.name+' · '+d.device_id;el('portal').textContent=d.portal_status;el('power').textContent=d.telemetry.actual_active_power_kw+' kW';el('reactive').textContent=d.telemetry.actual_reactive_power_kvar+' kvar';el('frequency').textContent=d.telemetry.grid_frequency_hz+' Hz';el('measurements').replaceChildren();for(const [label,value] of [['Spannung L1–L2',d.telemetry.grid_voltage_l12_volts+' V'],['Spannung L2–L3',d.telemetry.grid_voltage_l23_volts+' V'],['Spannung L3–L1',d.telemetry.grid_voltage_l31_volts+' V'],['Leistungsfaktor',d.telemetry.actual_cos_phi],['Reglerzustand',d.telemetry.controller_state_text],['Regelmodus',d.telemetry.active_control_mode_text]]){const row=document.createElement('tr');for(const text of [label,value]){const cell=document.createElement('td');cell.textContent=text;row.append(cell);}el('measurements').append(row);}el('configuration').textContent=JSON.stringify(d.configuration,null,2);el('updated').textContent='Zuletzt aktualisiert: '+new Date(d.timestamp).toLocaleTimeString();el('error').textContent='';}catch(e){el('error').textContent='Keine aktuellen Daten erreichbar. Angezeigte Werte können veraltet sein.';el('portal').textContent='Unbekannt';}finally{setTimeout(refresh,5000);}}refresh();
</script></main></html>"""


class SimulatorWeb:
    def __init__(self, gateway):
        self.gateway = gateway
        self.active = 0

    async def handle(self, reader, writer):
        if self.active >= 8:
            writer.close()
            await writer.wait_closed()
            return
        self.active += 1
        try:
            headers = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 5)
            method, path, version = headers.split(b"\r\n", 1)[0].split()
            status, kind, body = '200 OK', 'text/html; charset=utf-8', PAGE.encode()
            if method != b'GET':
                status, body = '405 Method Not Allowed', b'Read-only dashboard'
            elif path == b'/api/status':
                try:
                    telemetry = await asyncio.wait_for(self.gateway.controller_client.read_telemetry(), 3)
                    config = await asyncio.wait_for(self.gateway.controller_client.read_active_configuration(), 3)
                    body = json.dumps(dict(device_id=self.gateway.device_id, name=self.gateway.device_name,
                        portal_status=self.gateway.last_sync_status['status'], telemetry=telemetry,
                        configuration=config, timestamp=datetime.now(timezone.utc).isoformat())).encode()
                    kind = 'application/json'
                except Exception:
                    status, body = '503 Service Unavailable', b'Simulator unavailable'
            elif path != b'/':
                status, body = '404 Not Found', b'Not found'
            writer.write((f'HTTP/1.1 {status}\r\nContent-Type: {kind}\r\nContent-Length: {len(body)}\r\nConnection: close\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nContent-Security-Policy: default-src \'self\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; frame-ancestors \'none\'; base-uri \'none\'\r\n\r\n').encode()+body)
            await asyncio.wait_for(writer.drain(), 5)
        except (ValueError, OSError, asyncio.TimeoutError, asyncio.IncompleteReadError, asyncio.LimitOverrunError):
            pass
        finally:
            self.active -= 1
            writer.close()
            await writer.wait_closed()

    async def start(self, path):
        server = await asyncio.start_unix_server(self.handle, path, limit=8192)
        os.chmod(path, 0o666)
        return server
