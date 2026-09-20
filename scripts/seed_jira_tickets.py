import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db
from backend.jira_service import jira_service

def main():
    init_db()
    t1 = jira_service.create_ticket(
        summary="[FEAT] VDE-AR-N 4110 Netzstoerungs- und Ereignisprotokollierung (Schutzabschaltung)",
        description="Automatische Aufzeichnung von Grenzwertverletzungen (U > 1.10 Un, f < 49.8 Hz) mit hochaufloesendem Stoerschreiber-Log fuer den Netzbetreiber.",
        issue_type="Task",
        priority="High",
        labels=["vde4110", "telemetry", "continuous-improvement"]
    )

    t2 = jira_service.create_ticket(
        summary="[FEAT] Automatisierter PDF- und CSV-Inbetriebsetzungsbericht (E.9 VNB Konformitaet)",
        description="Generierung eines offiziellen VDE-AR-N 4110 Konformitaetsberichts fuer den Verteilnetzbetreiber (DSO) auf Knopfdruck als PDF.",
        issue_type="Task",
        priority="High",
        labels=["compliance", "reporting", "continuous-improvement"]
    )

    t3 = jira_service.create_ticket(
        summary="[FEAT] Multi-Inverter String-Level Monitoring und BESS Rack-Ueberwachung",
        description="Detailansicht fuer Wechselrichter-Einzelstrings (MPPT-Spannung, Strangstroeme, Wirkungsgrad) und Batteriespeicher-Rackzustaende.",
        issue_type="Task",
        priority="Medium",
        labels=["inverter", "bess", "monitoring"]
    )

    t4 = jira_service.create_question_ticket(
        question_title="Jira Verbindungsdaten und Roadmap-Priorisierung",
        question_details="Bitte hinterlegen Sie die Jira API-Zugangsdaten (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY, JIRA_DEFAULT_ASSIGNEE_ID) und priorisieren Sie die naechsten Umsetzungsschritte.",
        options=["1. VDE-AR-N 4110 Stoerungsrekorder", "2. PDF/CSV Konformitaetsbericht", "3. Inverter String-Monitoring"]
    )

    print(f"Successfully seeded Jira roadmap tickets:")
    print(f" - {t1['jira_key']}: {t1['summary']}")
    print(f" - {t2['jira_key']}: {t2['summary']}")
    print(f" - {t3['jira_key']}: {t3['summary']}")
    print(f" - {t4['jira_key']}: {t4['summary']}")

if __name__ == "__main__":
    main()
