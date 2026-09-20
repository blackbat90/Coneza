import sys
import os

# Set environment variables for testing
os.environ["CONFLUENCE_URL"] = "https://easy-eza.atlassian.net"
os.environ["CONFLUENCE_EMAIL"] = "ai@coneza.de"
os.environ["CONFLUENCE_API_TOKEN"] = "ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7"
os.environ["CONFLUENCE_SPACE"] = "EEPD"

sys.path.insert(0, ".")

from backend.confluence_service import confluence_service

print("Testing Confluence Service...")
print("Configured:", confluence_service.is_configured())

# 1. Log today's improvement 1: Energy Flow & Grid Parameters
res1 = confluence_service.log_daily_improvement(
    date_str="20.09.2026",
    feature_title="Energiefluss-Visualisierung & EZA-Netzparameter (White Theme)",
    details="Neues EZA-Dashboard nach coneza.de White-Design: Solar-Erzeugung, Eigenverbrauch, Batteriespeicher, Netzparameter (U L1-L3, Frequenz, Wirk-/Blindleistung, cos φ) und VDE-Regelkennlinien.",
    jira_key="EEP-46",
    commit_hash="e4add1fa",
    status="Live in Production"
)
print("Log 1 Result:", res1)

# 2. Log today's improvement 2: Jira Autonomous Integration
res2 = confluence_service.log_daily_improvement(
    date_str="20.09.2026",
    feature_title="Autonome Jira-Integration (ai@coneza.de) & Ticket-Automatisierung",
    details="Integration der Atlassian Jira Cloud REST API v3 über Postfach ai@coneza.de. Autonome Ticketerstellung bei Fragen, Fehlern oder Feature-Vorschlägen direkt zugewiesen an Shehzad Saleem.",
    jira_key="EEP-49",
    commit_hash="e906d21a",
    status="Live in Production"
)
print("Log 2 Result:", res2)
