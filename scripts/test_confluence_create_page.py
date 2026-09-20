import urllib.request
import urllib.error
import json
import base64
import ssl

JIRA_URL = "https://easy-eza.atlassian.net"
EMAIL = "ai@coneza.de"
API_TOKEN = "ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7"

auth_str = f"{EMAIL}:{API_TOKEN}"
b64_auth = base64.b64encode(auth_str.encode("ascii")).decode("ascii")

headers = {
    "Authorization": f"Basic {b64_auth}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

ctx = ssl.create_default_context()

page_payload = {
    "type": "page",
    "title": "Coneza Portal — System- & Architektur-Dokumentation",
    "space": {"key": "EEPD"},
    "ancestors": [{"id": "393341"}],
    "body": {
        "storage": {
            "value": """
<h2>Coneza Portal &amp; EZA-Reglersystem — Übersicht</h2>
<p>Dieses Dokument wird kontinuierlich durch den <strong>Coneza AI Assistant</strong> (<code>ai@coneza.de</code>) aktualisiert.</p>

<h3>1. System-Architektur</h3>
<table>
  <thead>
    <tr>
      <th>Komponente</th>
      <th>Technologie</th>
      <th>URL / Port</th>
      <th>Beschreibung</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Frontend</strong></td>
      <td>HTML5, Vanilla CSS, JS (White Theme)</td>
      <td><code>https://coneza.de/portal/</code></td>
      <td>EZA-Dashboard, Energiefluss-Visualisierung, Regelparameter, Jira-Ticket-Center</td>
    </tr>
    <tr>
      <td><strong>Backend</strong></td>
      <td>FastAPI, Python 3.11, Uvicorn</td>
      <td><code>http://localhost:9080/api</code></td>
      <td>REST-API, WebSocket Telemetrie, Modbus/MQTT Client, Jira/Confluence Bridge</td>
    </tr>
    <tr>
      <td><strong>Hardware-Controller</strong></td>
      <td>Phoenix Contact RFC 4072S / AXC F 2152</td>
      <td>192.168.1.10 (Modbus TCP)</td>
      <td>EZA-Regelung nach VDE-AR-N 4110 / 4120 / 4105</td>
    </tr>
  </tbody>
</table>

<h3>2. Energiefluss &amp; Regelungsparameter</h3>
<ul>
  <li><strong>Erzeugungsanlage (EZ):</strong> PV-Erzeugung, Eigenverbrauch, Batteriespeicher (SoC/Ladeleistung)</li>
  <li><strong>Netzwerkparameter:</strong> Netzspannung (L1-L3), Netzfrequenz (50,00 Hz), Wirkleistung P, Blindleistung Q, Power Factor cos(&phi;)</li>
  <li><strong>VDE-Regelkennlinien:</strong> Q(U), P(U), P(f), Blindleistungs-Sollwerte</li>
</ul>

<h3>3. Kontinuierliche Verbesserungs-Pipeline</h3>
<p>Alle Code-Änderungen, Fehlerkorrekturen und Feature-Erweiterungen werden:</p>
<ol>
  <li>In Git mit sauberer Commit-Historie versioniert</li>
  <li>Automatisch über Jira im Projekt <strong>EEP</strong> als Ticket erfasst</li>
  <li>Rückfragen oder Genehmigungen direkt an Shehzad Saleem zugewiesen</li>
  <li>In dieser Confluence-Dokumentation strukturiert festgehalten</li>
</ol>
""",
            "representation": "storage"
        }
    }
}

print("--- Creating/Updating Documentation Page in Confluence EEPD ---")
url = f"{JIRA_URL}/wiki/rest/api/content"
req = urllib.request.Request(url, data=json.dumps(page_payload).encode("utf-8"), headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        print(f"Success! Page created with ID: {res_data.get('id')}")
        print(f"Title: {res_data.get('title')}")
        print(f"Link: {JIRA_URL}/wiki" + res_data.get('_links', {}).get('webui', ''))
except urllib.error.HTTPError as e:
    err_msg = e.read().decode("utf-8")
    print(f"HTTP Error {e.code}: {err_msg}")
    # If title already exists, find existing page and update it
    if "already exists" in err_msg or "title" in err_msg.lower():
        print("Page might already exist, checking existing pages...")
except Exception as e:
    print(f"Error: {e}")
