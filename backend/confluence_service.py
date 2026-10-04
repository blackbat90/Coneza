"""
Confluence Service for Coneza Operations Portal.
Fetches, synchronizes, and extracts product requirements, technical specifications,
and grid operator landscape directly from Atlassian Confluence REST API v1/v2.
Also handles autonomous changelog logging and documentation updates.
"""

import os
import json
import base64
import re
import ssl
import logging
from html import unescape
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

logger = logging.getLogger("coneza_confluence_service")

# Environment & Config Loading
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL", "").rstrip("/")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL", "")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "EEPD")

# Fallback to local jira_config.json if not in env
cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jira_config.json")
if os.path.exists(cfg_path):
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            CONFLUENCE_URL = CONFLUENCE_URL or cfg.get("JIRA_URL", "").rstrip("/")
            CONFLUENCE_EMAIL = CONFLUENCE_EMAIL or cfg.get("JIRA_EMAIL", "")
            CONFLUENCE_API_TOKEN = CONFLUENCE_API_TOKEN or cfg.get("JIRA_API_TOKEN", "")
            CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY") or cfg.get("CONFLUENCE_SPACE_KEY", "EEPD")
    except Exception as e:
        logger.warning(f"Could not load jira_config.json: {e}")

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "confluence_cache.json")


def clean_html_content(raw_html: str) -> str:
    """Strips HTML tags and converts entities into clean Markdown-style plain text."""
    if not raw_html:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', raw_html)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<li[^>]*>', '• ', text)
    text = re.sub(r'<h[1-6][^>]*>', '\n### ', text)
    text = re.sub(r'</h[1-6]>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(line for line in lines if line)


class ConfluenceService:
    """Service to interact with Atlassian Confluence REST API."""

    def __init__(self):
        self.url = CONFLUENCE_URL
        self.email = CONFLUENCE_EMAIL
        self.token = CONFLUENCE_API_TOKEN
        self.space_key = CONFLUENCE_SPACE_KEY
        self.cache_path = CACHE_FILE
        self.ctx = ssl.create_default_context()

    def is_configured(self) -> bool:
        return bool(self.url and self.email and self.token)

    def _get_auth_header(self) -> str:
        raw = f"{self.email}:{self.token}".encode("utf-8")
        return f"Basic {base64.b64encode(raw).decode('utf-8')}"

    def get_spaces(self) -> List[Dict[str, Any]]:
        """Retrieves list of accessible Confluence spaces."""
        if not self.is_configured():
            logger.warning("Confluence service not configured with URL/Token.")
            return []

        api_endpoint = f"{self.url}/wiki/rest/api/space"
        req = urllib.request.Request(
            api_endpoint,
            headers={
                "Authorization": self._get_auth_header(),
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=10, context=self.ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [
                    {
                        "key": s.get("key"),
                        "name": s.get("name"),
                        "type": s.get("type")
                    }
                    for s in data.get("results", [])
                ]
        except Exception as e:
            logger.error(f"Failed to fetch Confluence spaces: {e}")
            return []

    def get_space_pages(self, space_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves overview of pages in a space for UI display."""
        target_space = space_key or self.space_key
        if not self.is_configured():
            return [
                {"id": "mock-1", "title": "Coneza Portal — System- & Architektur-Dokumentation", "type": "page", "version": 1},
                {"id": "mock-2", "title": "EZA-Regler & VDE-AR-N 4110 Spezifikation", "type": "page", "version": 1},
                {"id": "mock-3", "title": "Coneza Portal — Tägliches Verbesserungs- & Changelog", "type": "page", "version": 3}
            ]

        endpoint = f"{self.url}/wiki/rest/api/content?spaceKey={target_space}&limit=50&expand=version"
        req = urllib.request.Request(
            endpoint,
            headers={"Authorization": self._get_auth_header(), "Accept": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10, context=self.ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = []
                for p in data.get("results", []):
                    pages.append({
                        "id": p.get("id"),
                        "title": p.get("title"),
                        "type": p.get("type"),
                        "version": p.get("version", {}).get("number", 1),
                        "url": f"{self.url}/wiki" + p.get("_links", {}).get("webui", "")
                    })
                return pages
        except Exception as e:
            logger.error(f"Failed to fetch pages for space {target_space}: {e}")
            return []

    def fetch_all_pages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches documentation pages with storage body content across accessible spaces."""
        if not self.is_configured():
            return self._load_from_cache()

        api_endpoint = f"{self.url}/wiki/rest/api/content?limit={limit}&expand=body.storage,version"
        req = urllib.request.Request(
            api_endpoint,
            headers={
                "Authorization": self._get_auth_header(),
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15, context=self.ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = []
                for p in data.get("results", []):
                    body_raw = p.get("body", {}).get("storage", {}).get("value", "")
                    clean_text = clean_html_content(body_raw)
                    pages.append({
                        "id": p.get("id"),
                        "title": p.get("title"),
                        "type": p.get("type"),
                        "version": p.get("version", {}).get("number", 1),
                        "content": clean_text,
                        "char_count": len(clean_text)
                    })

                self._save_to_cache(pages)
                return pages
        except Exception as e:
            logger.error(f"Failed to fetch pages from Confluence API: {e}. Falling back to cache.")
            return self._load_from_cache()

    def get_page_by_title(self, title: str, space_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetches a specific page by title and space."""
        if not self.is_configured():
            return None

        target_space = space_key or self.space_key
        encoded_title = urllib.parse.quote(title)
        endpoint = f"{self.url}/wiki/rest/api/content?spaceKey={target_space}&title={encoded_title}&expand=body.storage,version"
        req = urllib.request.Request(
            endpoint,
            headers={"Authorization": self._get_auth_header(), "Accept": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10, context=self.ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                return results[0] if results else None
        except Exception as e:
            logger.error(f"Error fetching page '{title}': {e}")
            return None

    def create_or_update_page(self, title: str, html_content: str, space_key: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new page or updates an existing one with new HTML content."""
        if not self.is_configured():
            logger.warning(f"Simulating Confluence page '{title}' update (not configured).")
            return {"status": "simulated", "title": title}

        target_space = space_key or self.space_key
        existing_page = self.get_page_by_title(title, target_space)

        if existing_page:
            page_id = existing_page["id"]
            current_version = existing_page["version"]["number"]
            endpoint = f"{self.url}/wiki/rest/api/content/{page_id}"

            payload = {
                "id": page_id,
                "type": "page",
                "title": title,
                "space": {"key": target_space},
                "body": {
                    "storage": {
                        "value": html_content,
                        "representation": "storage"
                    }
                },
                "version": {"number": current_version + 1}
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": self._get_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                method="PUT"
            )

            try:
                with urllib.request.urlopen(req, context=self.ctx) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "status": "updated",
                        "id": page_id,
                        "title": title,
                        "version": current_version + 1,
                        "url": f"{self.url}/wiki" + res_data.get("_links", {}).get("webui", "")
                    }
            except Exception as e:
                logger.error(f"Failed to update Confluence page '{title}': {e}")
                return {"status": "error", "message": str(e)}
        else:
            endpoint = f"{self.url}/wiki/rest/api/content"
            payload = {
                "type": "page",
                "title": title,
                "space": {"key": target_space},
                "body": {
                    "storage": {
                        "value": html_content,
                        "representation": "storage"
                    }
                }
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": self._get_auth_header(),
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
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
        """Appends or updates the continuous improvement changelog page in Confluence."""
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
"""
        results["architecture"] = self.create_or_update_page("Coneza Portal — System- & Architektur-Dokumentation", arch_html)
        return {"status": "success", "results": results}

    def _save_to_cache(self, pages: List[Dict[str, Any]]) -> None:
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(pages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save Confluence cache: {e}")

    def _load_from_cache(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not read Confluence cache: {e}")
        return []

    def get_key_requirements_summary(self) -> Dict[str, Any]:
        """Extracts high-level product requirements and architectural decisions."""
        pages = self.fetch_all_pages()
        page_dict = {p["title"]: p["content"] for p in pages if "title" in p}

        return {
            "total_pages": len(pages),
            "architecture_features": page_dict.get("Architecture and Features", ""),
            "edge_cases": page_dict.get("Edge Cases", ""),
            "hardware_platform": page_dict.get("Hardware Platform definition", ""),
            "competitor_insights": page_dict.get("Competitor analysis", ""),
            "vde_specification": page_dict.get("EZA-Regler & VDE-AR-N 4110 Spezifikation", ""),
            "has_dso_database": "Mittelspannung" in page_dict
        }


# Global singleton instance
confluence_service = ConfluenceService()
