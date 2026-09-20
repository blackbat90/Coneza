import unittest
from backend.jira_service import jira_service
from backend.database import init_db

class TestJiraService(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_01_create_local_ticket(self):
        res = jira_service.create_ticket(
            summary="Continuous Improvement: Add VDE-AR-N 4110 Disturbance Logger",
            description="Autonomous ticket tracking grid event log recording.",
            issue_type="Task",
            priority="High",
            labels=["vde4110", "telemetry"]
        )
        self.assertIn("jira_key", res)
        self.assertEqual(res["status"], "OPEN")
        self.assertIn("id", res)

    def test_02_create_question_ticket(self):
        res = jira_service.create_question_ticket(
            question_title="Sollwert-Vorgabe für Q(U) Totband U2/U3",
            question_details="Soll das Totband standardmäßig bei 97%-103% oder 95%-105% liegen?",
            options=["97% - 103% Un (VDE-AR-N 4110 Standard)", "95% - 105% Un (Erweitertes Totband)"]
        )
        self.assertIn("jira_key", res)
        self.assertTrue(res["summary"].startswith("[Rückfrage / Freigabe]"))

    def test_03_list_tickets(self):
        tickets = jira_service.list_tickets(limit=10)
        self.assertIsInstance(tickets, list)
        self.assertGreaterEqual(len(tickets), 2)
        keys = [t["jira_key"] for t in tickets]
        self.assertTrue(any("LOCAL" in k or "CON" in k for k in keys))

if __name__ == "__main__":
    unittest.main()
