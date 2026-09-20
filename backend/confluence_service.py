"""
Confluence Service for Coneza Operations Portal.
Handles automated documentation synchronization, architectural specifications,
and daily improvement logging in Atlassian Confluence Cloud via REST API.
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error
import ssl

logger = logging.getLogger("coneza_confluence_service")

# Environment configuration
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", os.getenv("JIRA_URL", "https://easy-eza.atlassian.net")).rstrip("/")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL", os.getenv("JIRA_EMAIL", "ai@coneza.de"))
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", os.getenv("JIRA_API_TOKEN", ""))
CONFLUENCE_SPACE = os.getenv("CONFLUENCE_SPACE", "EEPD")

# Fallback to local jira_config.json if token not in env
if not CONFLUENCE_API_TOKEN:
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jira_config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                CONFLUENCE_URL = CONFLUENCE_URL or cfg.get("JIRA_URL", "").rstrip("/")
                CONFLUENCE_EMAIL = CONFLUENCE_EMAIL or cfg.get("JIRA_EMAIL", "")
                CONFLUENCE_API_TOKEN = CONFLUENCE_API_TOKEN or cfg.get("JIRA_API_TOKEN", "")
        except Exception:
            pass



class ConfluenceService:
    """Automates technical documentation and daily improvement logging in Confluence."""

    def __init__(self):
        self.url = CONFLUENCE_URL
        self.email = CONFLUENCE_EMAIL
        self.token = CONFLUENCE_API_TOKEN
        self.space_key = CONFLUENCE_SPACE
        self.ctx = ssl.create_default_context()

    def is_configured(self) -> bool:
        """Checks if remote Confluence API credentials are provided."""
        return bool(self.url and self.email and self.token)

    def _get_headers(self) -> Dict[str, str]:
        raw = f"{self.email}:{self.token}".encode("utf-8")
        b64 = base64.b64encode(raw).decode("utf-8")
        return {
            "Authorization": f"Basic {b64}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_space_pages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists pages in the configured Confluence space."""
        if not self.is_configured():
            return []
        try:
            endpoint = f"{self.url}/wiki/rest/api/content?spaceKey={self.space_key}&limit={limit}&expand=version,metadata"
            req = urllib.request.Request(endpoint, headers=self._get_headers())
            with urllib.request.urlopen(req, context=self.ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = []
                for p in data.get("results", []):
                    pages.append({
                        "id": p.get("id"),
                        "title": p.get("title"),
                        "status": p.get("status"),
                        "version": p.get("version", {}).get("number", 1),
                        "url": f"{self.url}/wiki" + p.get("_links", {}).get("webui", "")
                    })
                return pages
        except Exception as e:
            logger.error(f"Failed to fetch Confluence pages: {e}")
            return []

    def get_page_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Finds a page by title in the configured space."""
        if not self.is_configured():
            return None
        try:
            encoded_title = urllib.parse.quote(title)
            endpoint = f"{self.url}/wiki/rest/api/content?spaceKey={self.space_key}&title={encoded_title}&expand=version,body.storage,ancestors"
            req = urllib.request.Request(endpoint, headers=self._get_headers())
            with urllib.request.urlopen(req, context=self.ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                if results:
                    return results[0]
                return None
        except Exception as e:
            logger.error(f"Error querying Confluence page by title '{title}': {e}")
            return None

    def create_or_update_page(
        self,
        title: str,
        body_html: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a new page or updates the existing one with next version number."""
        if not self.is_configured():
            return {"status": "skipped", "message": "Confluence not configured"}

        existing = self.get_page_by_title(title)

        if existing:
            # Update existing page
            page_id = existing["id"]
            current_ver = existing.get("version", {}).get("number", 1)
            new_ver = current_ver + 1

            payload = {
                "id": page_id,
                "type": "page",
                "title": title,
                "space": {"key": self.space_key},
                "version": {"number": new_ver},
                "body": {
                    "storage": {
                        "value": body_html,
                        "representation": "storage"
                    }
                }
            }
            if parent_id:
                payload["ancestors"] = [{"id": parent_id}]

            endpoint = f"{self.url}/wiki/rest/api/content/{page_id}"
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=self._get_headers(),
                method="PUT"
            )
            try:
                with urllib.request.urlopen(req, context=self.ctx) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "status": "updated",
                        "id": res_data.get("id"),
                        "title": title,
                        "version": new_ver,
                        "url": f"{self.url}/wiki" + res_data.get("_links", {}).get("webui", "")
                    }
            except Exception as e:
                logger.error(f"Failed to update Confluence page {page_id}: {e}")
                return {"status": "error", "message": str(e)}

        else:
            # Create new page
            payload = {
                "type": "page",
                "title": title,
                "space": {"key": self.space_key},
                "body": {
                    "storage": {
                        "value": body_html,
                        "representation": "storage"
                    }
                }
            }
            if parent_id:
                payload["ancestors"] = [{"id": parent_id}]

            endpoint = f"{self.url}/wiki/rest/api/content"
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=self._get_headers(),
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, context=self.ctx) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "status": "created",
                        "id": res_data.get("id"),
                        "title": title,
                        "version": 1,
                        "url": f"{self.url}/wiki" + res_data.get("_links", {}).get("webui", "")
                    }
            except Exception as e:
                logger.error(f"Failed to create Confluence page '{title}': {e}")
                return {"status": "error", "message": str(e)}

    def log_daily_improvement(
        self,
        date_str: str,
        feature_title: str,
        details: str,
        jira_key: Optional[str] = None,
        commit_hash: Optional[str] = None,
        status: str = "Live in Production"
    ) -> Dict[str, Any]:
        """
        Appends or updates the continuous improvement changelog page in Confluence.
        """
        page_title = "Coneza Portal — Tägliches Verbesserungs- & Changelog"
        existing = self.get_page_by_title(page_title)

        entry_html = f"""
<tr>
  <td><strong>{date_str}</strong></td>
  <td><strong>{feature_title}</strong><br/>{details}</td>
  <td><a href="{self.url}/browse/{jira_key}">{jira_key}</a></td>
  <td><code>{commit_hash or 'HEAD'}</code></td>
  <td><span style="color: #059669; font-weight: bold;">{status}</span></td>
</tr>
"""

        if existing:
            current_body = existing.get("body", {}).get("storage", {}).get("value", "")
            if "<tbody>" in current_body:
                # Prepend the new entry to the top of tbody
                updated_body = current_body.replace("<tbody>", f"<tbody>{entry_html}", 1)
            else:
                updated_body = current_body + f"<table><tbody>{entry_html}</tbody></table>"
        else:
            updated_body = f"""
<h2>Coneza Portal — Tägliches Verbesserungs- &amp; Changelog</h2>
<p>Dieses Dokument wird durch den <strong>Coneza AI Assistant</strong> (<code>ai@coneza.de</code>) kontinuierlich gepflegt.
Jede Verbesserung wird mit Datum, Jira-Referenz und Git-Commit transparent dokumentiert.</p>

<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #f3f4f6;">
      <th style="width: 15%;">Datum</th>
      <th style="width: 45%;">Verbesserung / Feature</th>
      <th style="width: 15%;">Jira-Ticket</th>
      <th style="width: 10%;">Commit</th>
      <th style="width: 15%;">Status</th>
    </tr>
  </thead>
  <tbody>
    {entry_html}
  </tbody>
</table>
"""
        return self.create_or_update_page(page_title, updated_body)

    def sync_all_documentation(self) -> Dict[str, Any]:
        """Ensures all standard documentation pages exist and are up to date."""
        results = {}

        # 1. System & Architecture Overview
        arch_html = """
<h2>Coneza Portal &amp; EZA-Reglersystem — Systemarchitektur</h2>
<p>Dieses Dokument wird kontinuierlich durch den <strong>Coneza AI Assistant</strong> (<code>ai@coneza.de</code>) aktualisiert.</p>

<h3>1. System-Architektur</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #f3f4f6;">
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
      <td>EZA-Dashboard, Energiefluss-Visualisierung, Regelparameter, Jira- &amp; Confluence-Integration</td>
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
"""
        results["architecture"] = self.create_or_update_page("Coneza Portal — System- & Architektur-Dokumentation", arch_html)

        # 2. Hardware Specification
        hw_html = """
<h2>EZA-Regler &amp; VDE-AR-N 4110 Spezifikation</h2>
<p>Dokumentiert die Schnittstellen und Regelungsparameter des Coneza EZA-Portals zur Steuerung von Erzeugungsanlagen (EZ) am Mittel- und Hochspannungsnetz.</p>

<h3>1. Unterstützte Controller-Hardware</h3>
<ul>
  <li><strong>Phoenix Contact RFC 4072S:</strong> High-Performance Safety-SPS für zentrale Netzregelung nach VDE-AR-N 4110</li>
  <li><strong>Phoenix Contact AXC F 2152 / 3152:</strong> PLCnext Controller für Edge-Telemetrie und Modbus TCP Gateway</li>
</ul>

<h3>2. Kommunikationsschnittstellen &amp; Registerbelegung (Modbus TCP)</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #f3f4f6;">
      <th>Modbus Register</th>
      <th>Signalname</th>
      <th>Einheit</th>
      <th>Typ</th>
      <th>Funktion</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>30001</td><td>Grid_Voltage_L1_N</td><td>V</td><td>Float32</td><td>Effektivspannung Außenleiter L1</td></tr>
    <tr><td>30003</td><td>Grid_Voltage_L2_N</td><td>V</td><td>Float32</td><td>Effektivspannung Außenleiter L2</td></tr>
    <tr><td>30005</td><td>Grid_Voltage_L3_N</td><td>V</td><td>Float32</td><td>Effektivspannung Außenleiter L3</td></tr>
    <tr><td>30007</td><td>Grid_Frequency</td><td>Hz</td><td>Float32</td><td>Netzfrequenz (Nennwert 50,00 Hz)</td></tr>
    <tr><td>30009</td><td>Active_Power_P</td><td>kW</td><td>Float32</td><td>Gesamte Wirkleistung am Netzverknüpfungspunkt (NAP)</td></tr>
    <tr><td>30011</td><td>Reactive_Power_Q</td><td>kvar</td><td>Float32</td><td>Gesamte Blindleistung am NAP</td></tr>
    <tr><td>30013</td><td>Power_Factor_cosPhi</td><td>-</td><td>Float32</td><td>Leistungsfaktor cos(&phi;)</td></tr>
    <tr><td>40001</td><td>Q_Control_Mode</td><td>Enum</td><td>UInt16</td><td>0=Off, 1=Q(U), 2=cosPhi(P), 3=Q-Festwert</td></tr>
    <tr><td>40002</td><td>P_Limit_Setpoint</td><td>%</td><td>Float32</td><td>Wirkleistungsbegrenzung (0..100% P_nenn)</td></tr>
  </tbody>
</table>
"""
        results["hardware_spec"] = self.create_or_update_page("EZA-Regler & VDE-AR-N 4110 Spezifikation", hw_html)

        return {"status": "success", "results": results}


confluence_service = ConfluenceService()
