"""
Jira Service for Coneza Operations Portal.
Handles automated ticket creation, issue tracking, and assigning review/question tickets
to the product owner / lead engineer via Atlassian Jira REST API v3.
"""

import os
import json
import base64
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

from backend.database import get_connection

logger = logging.getLogger("coneza_jira_service")

# Environment configuration
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "EEP")
JIRA_DEFAULT_ASSIGNEE_ID = os.getenv("JIRA_DEFAULT_ASSIGNEE_ID", "")

# Fallback to local jira_config.json if available
if not (JIRA_URL and JIRA_EMAIL and JIRA_API_TOKEN):
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jira_config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                JIRA_URL = JIRA_URL or cfg.get("JIRA_URL", "").rstrip("/")
                JIRA_EMAIL = JIRA_EMAIL or cfg.get("JIRA_EMAIL", "")
                JIRA_API_TOKEN = JIRA_API_TOKEN or cfg.get("JIRA_API_TOKEN", "")
                JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY") or cfg.get("JIRA_PROJECT_KEY", "EEP")
                JIRA_DEFAULT_ASSIGNEE_ID = JIRA_DEFAULT_ASSIGNEE_ID or cfg.get("JIRA_DEFAULT_ASSIGNEE_ID", "")
        except Exception:
            pass

class JiraService:
    """Automates ticket creation, sync, and user assignment for portal enhancements."""

    def __init__(self):
        self.url = JIRA_URL
        self.email = JIRA_EMAIL
        self.token = JIRA_API_TOKEN
        self.project_key = JIRA_PROJECT_KEY
        self.assignee_id = JIRA_DEFAULT_ASSIGNEE_ID

    def is_configured(self) -> bool:
        """Checks if remote Jira API credentials are provided."""
        return bool(self.url and self.email and self.token)

    def _get_auth_header(self) -> str:
        raw = f"{self.email}:{self.token}".encode("utf-8")
        return f"Basic {base64.b64encode(raw).decode('utf-8')}"

    def create_ticket(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        assignee_id: Optional[str] = None,
        labels: Optional[List[str]] = None,
        plant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a ticket in Jira if configured; always records in local SQLite for auditability.
        """
        ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        labels = labels or ["coneza-portal", "automated"]
        assignee = assignee_id or self.assignee_id

        jira_key = None
        synced = 0

        # Try posting to Atlassian Jira Cloud REST API v3
        if self.is_configured():
            try:
                endpoint = f"{self.url}/rest/api/3/issue"
                adf_description = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }

                fields: Dict[str, Any] = {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": adf_description,
                    "issuetype": {"name": issue_type},
                    "labels": labels
                }

                if assignee:
                    fields["assignee"] = {"id": assignee}

                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps({"fields": fields}).encode("utf-8"),
                    headers={
                        "Authorization": self._get_auth_header(),
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    jira_key = resp_data.get("key")
                    synced = 1
                    logger.info(f"Created Jira ticket {jira_key}: {summary}")
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                logger.warning(f"Jira API HTTP error {e.code}: {err_body}")
            except Exception as e:
                logger.warning(f"Failed to push to Jira: {e}")

        # Store in local database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jira_tickets (
                id, jira_key, summary, description, issue_type,
                priority, status, assignee, labels_json, plant_id,
                created_at, updated_at, synced_with_jira
            ) VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            jira_key or f"{self.project_key}-LOCAL-{ticket_id[-4:].upper()}",
            summary,
            description,
            issue_type,
            priority,
            assignee or "Unassigned",
            json.dumps(labels),
            plant_id,
            now,
            now,
            synced
        ))
        conn.commit()
        conn.close()

        return {
            "id": ticket_id,
            "jira_key": jira_key or f"{self.project_key}-LOCAL-{ticket_id[-4:].upper()}",
            "summary": summary,
            "status": "OPEN",
            "assignee": assignee or "Unassigned",
            "synced_with_jira": bool(synced)
        }

    def create_question_ticket(
        self,
        question_title: str,
        question_details: str,
        options: Optional[List[str]] = None,
        plant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Specialized helper to create an actionable question ticket assigned to the user."""
        desc = f"{question_details}\n\n"
        if options:
            desc += "Entscheidungsoptionen:\n"
            for i, opt in enumerate(options, 1):
                desc += f"{i}. {opt}\n"
        desc += "\nBitte weisen Sie das Ticket nach Ihrer Entscheidung zurück oder kommentieren Sie Ihre Freigabe."

        return self.create_ticket(
            summary=f"[Rückfrage / Freigabe] {question_title}",
            description=desc,
            issue_type="Task",
            priority="High",
            labels=["user-question", "coneza-portal", "requires-user-action"],
            plant_id=plant_id
        )

    def list_tickets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists tracked tickets from SQLite."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, jira_key, summary, description, issue_type, priority,
                   status, assignee, labels_json, plant_id, created_at, synced_with_jira
            FROM jira_tickets
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            item = dict(r)
            item["labels"] = json.loads(item["labels_json"]) if item["labels_json"] else []
            del item["labels_json"]
            results.append(item)
        return results

jira_service = JiraService()
