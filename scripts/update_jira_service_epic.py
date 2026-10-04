import os
import re

JIRA_FILE = os.path.join(os.path.dirname(__file__), "..", "backend", "jira_service.py")

with open(JIRA_FILE, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update config vars
old_vars = """JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "EEP")
JIRA_DEFAULT_ASSIGNEE_ID = os.getenv("JIRA_DEFAULT_ASSIGNEE_ID", "")"""

new_vars = """JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "EEP")
JIRA_DEFAULT_ASSIGNEE_ID = os.getenv("JIRA_DEFAULT_ASSIGNEE_ID", "")
JIRA_DEFAULT_EPIC_KEY = os.getenv("JIRA_DEFAULT_EPIC_KEY", "EEP-94")"""

if old_vars in code and "JIRA_DEFAULT_EPIC_KEY" not in code:
    code = code.replace(old_vars, new_vars, 1)
    print("Added JIRA_DEFAULT_EPIC_KEY variable")

# Also check cfg loading block
old_cfg = """                JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY") or cfg.get("JIRA_PROJECT_KEY", "EEP")
                JIRA_DEFAULT_ASSIGNEE_ID = JIRA_DEFAULT_ASSIGNEE_ID or cfg.get("JIRA_DEFAULT_ASSIGNEE_ID", "")"""

new_cfg = """                JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY") or cfg.get("JIRA_PROJECT_KEY", "EEP")
                JIRA_DEFAULT_ASSIGNEE_ID = JIRA_DEFAULT_ASSIGNEE_ID or cfg.get("JIRA_DEFAULT_ASSIGNEE_ID", "")
                JIRA_DEFAULT_EPIC_KEY = os.getenv("JIRA_DEFAULT_EPIC_KEY") or cfg.get("JIRA_DEFAULT_EPIC_KEY", "EEP-94")"""

if old_cfg in code and "JIRA_DEFAULT_EPIC_KEY =" not in code:
    code = code.replace(old_cfg, new_cfg, 1)
    print("Updated cfg loading for JIRA_DEFAULT_EPIC_KEY")

# 2. Update __init__
old_init = """        self.project_key = JIRA_PROJECT_KEY
        self.assignee_id = JIRA_DEFAULT_ASSIGNEE_ID"""

new_init = """        self.project_key = JIRA_PROJECT_KEY
        self.assignee_id = JIRA_DEFAULT_ASSIGNEE_ID
        self.default_epic_key = JIRA_DEFAULT_EPIC_KEY or "EEP-94\""""

if old_init in code and "self.default_epic_key" not in code:
    code = code.replace(old_init, new_init, 1)
    print("Added self.default_epic_key in __init__")

# 3. Update create_ticket signature and parent field
old_sig = """    def create_ticket(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        assignee_id: Optional[str] = None,
        labels: Optional[List[str]] = None,
        plant_id: Optional[str] = None
    ) -> Dict[str, Any]:"""

new_sig = """    def create_ticket(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        assignee_id: Optional[str] = None,
        labels: Optional[List[str]] = None,
        plant_id: Optional[str] = None,
        epic_key: Optional[str] = None
    ) -> Dict[str, Any]:"""

if old_sig in code:
    code = code.replace(old_sig, new_sig, 1)
    print("Updated create_ticket signature with epic_key")

old_fields = """                fields: Dict[str, Any] = {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": adf_description,
                    "issuetype": {"name": issue_type},
                    "labels": labels
                }"""

new_fields = """                target_epic = epic_key or self.default_epic_key or "EEP-94"
                fields: Dict[str, Any] = {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": adf_description,
                    "issuetype": {"name": issue_type},
                    "labels": labels
                }

                # Link all AI / portal tasks to Epic (default: EEP-94)
                if target_epic and issue_type.lower() != "epic":
                    fields["parent"] = {"key": target_epic}"""

if old_fields in code:
    code = code.replace(old_fields, new_fields, 1)
    print("Updated fields with parent epic link")

# 4. Update database insertion & return dict
old_insert = """            INSERT INTO jira_tickets (
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
        ))"""

new_insert = """            INSERT INTO jira_tickets (
                id, jira_key, summary, description, issue_type,
                priority, status, assignee, labels_json, plant_id,
                created_at, updated_at, synced_with_jira, epic_key
            ) VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, ?, ?, ?)
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
            synced,
            epic_key or self.default_epic_key or "EEP-94"
        ))"""

if old_insert in code:
    code = code.replace(old_insert, new_insert, 1)
    print("Updated SQL insert with epic_key")

old_return = """        return {
            "id": ticket_id,
            "jira_key": jira_key or f"{self.project_key}-LOCAL-{ticket_id[-4:].upper()}",
            "summary": summary,
            "status": "OPEN",
            "assignee": assignee or "Unassigned",
            "synced_with_jira": bool(synced)
        }"""

new_return = """        return {
            "id": ticket_id,
            "jira_key": jira_key or f"{self.project_key}-LOCAL-{ticket_id[-4:].upper()}",
            "summary": summary,
            "status": "OPEN",
            "assignee": assignee or "Unassigned",
            "epic_key": epic_key or self.default_epic_key or "EEP-94",
            "synced_with_jira": bool(synced)
        }"""

if old_return in code:
    code = code.replace(old_return, new_return, 1)
    print("Updated return dict with epic_key")

# 5. Update list_tickets SELECT query
old_select = """            SELECT id, jira_key, summary, description, issue_type, priority,
                   status, assignee, labels_json, plant_id, created_at, synced_with_jira
            FROM jira_tickets"""

new_select = """            SELECT id, jira_key, summary, description, issue_type, priority,
                   status, assignee, labels_json, plant_id, created_at, synced_with_jira, epic_key
            FROM jira_tickets"""

if old_select in code:
    code = code.replace(old_select, new_select, 1)
    print("Updated list_tickets SELECT with epic_key")

# 6. Add create_issue alias
if "def create_issue(" not in code:
    alias_code = """    def create_issue(self, *args, **kwargs) -> Dict[str, Any]:
        \"\"\"Alias for create_ticket.\"\"\"
        return self.create_ticket(*args, **kwargs)
"""
    target_pos = "jira_service = JiraService()"
    code = code.replace(target_pos, alias_code + "\n" + target_pos, 1)
    print("Added create_issue alias")

with open(JIRA_FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated jira_service.py successfully!")
