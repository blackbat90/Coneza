"""
Test Suite for coneza Unattended Continuous Improvement Engine & Knowledge Pipeline
"""

import os
import json
import uuid
import unittest
from fastapi.testclient import TestClient

from backend.main import app, seed_default_users
from backend.database import init_db, get_connection
from backend.continuous_improver import continuous_improver

class TestContinuousImprover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_path = os.path.join(os.path.dirname(__file__), "test_improver.db")
        os.environ["CONEZA_DB_PATH"] = cls.db_path
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except Exception:
                pass
        init_db()
        seed_default_users()
        cls.client = TestClient(app)

        # Login as Super User
        login_resp = cls.client.post("/api/auth/login", json={"username": "admin", "password": "conezaAdmin2026!"})
        cls.token = login_resp.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except Exception:
                pass

    def test_01_unattended_document_processing(self):
        """Tests that direct ingestion updates knowledge base and synthesizes auto-optimized config."""
        conn = get_connection()
        cursor = conn.cursor()

        # Insert a mock E.9 document with Bayernwerk grid specifications
        doc_id = f"doc_test_{uuid.uuid4().hex[:6]}"
        ocr_mock = {
            "detected_type": "E9",
            "total_pages": 1,
            "full_text": "Netzanschlussvertrag Bayernwerk Netz GmbH VDE-AR-N 4110 Mittelspannung 20 kV Q(U) Regelung",
            "extracted_entities": {
                "active_power_kw": 2400.0,
                "apparent_power_kva": 2500.0,
                "grid_voltage_v": 20000.0,
                "reactive_mode": "Q(U)"
            }
        }
        cursor.execute("""
            INSERT INTO documents (id, device_id, doc_type, filename, file_path, ocr_data_json)
            VALUES (?, 'coneza-edge-solar-park-01', 'E9', 'bayernwerk_e9_setpoints.pdf', '/tmp/mock.pdf', ?)
        """, (doc_id, json.dumps(ocr_mock)))
        conn.commit()
        conn.close()

        # Run unattended processing
        result = continuous_improver.process_uploaded_document_unattended(doc_id, "coneza-edge-solar-park-01")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["doc_id"], doc_id)
        self.assertTrue(len(result["improvements"]) > 0)

        # Verify knowledge base was populated
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_items WHERE pattern_key = 'DSO::Bayernwerk_Netz_GmbH'")
        dso_item = cursor.fetchone()
        self.assertIsNotNone(dso_item)
        self.assertEqual(dso_item["category"], "DSO_PROFILE")

        cursor.execute("SELECT * FROM knowledge_items WHERE pattern_key = 'BENCHMARK::PV_INVERTER_RATIO'")
        ratio_item = cursor.fetchone()
        self.assertIsNotNone(ratio_item)

        # Verify pipeline events were logged
        cursor.execute("SELECT COUNT(*) FROM pipeline_events WHERE event_type = 'UNATTENDED_INGEST'")
        ingest_count = cursor.fetchone()[0]
        self.assertGreaterEqual(ingest_count, 1)

        cursor.execute("SELECT COUNT(*) FROM pipeline_events WHERE event_type = 'CONFIG_AUTO_OPTIMIZED'")
        opt_count = cursor.fetchone()[0]
        self.assertGreaterEqual(opt_count, 1)

        # Verify auto-optimized draft config has VDE-AR-N 4110 safeguards
        cursor.execute("SELECT parameters_json FROM eza_configurations WHERE device_id = 'coneza-edge-solar-park-01'")
        cfg_row = cursor.fetchone()
        self.assertIsNotNone(cfg_row)
        cfg_params = json.loads(cfg_row["parameters_json"])

        # Check Q(U) deadband optimizations
        qu = cfg_params.get("q_u_curve", {})
        self.assertEqual(qu.get("u2_percent"), 97.0)
        self.assertEqual(qu.get("u3_percent"), 103.0)

        # Check ramp rate optimization
        self.assertEqual(cfg_params.get("p_ramp_rate_kw_per_sec"), 100.0)

        # Check frequency droop
        pf = cfg_params.get("p_f_droop", {})
        self.assertEqual(pf.get("overfreq_start_hz"), 50.20)
        self.assertEqual(pf.get("underfreq_start_hz"), 49.80)

        conn.close()

    def test_02_improver_telemetry_endpoint(self):
        """Tests GET /api/improver/status API endpoint."""
        resp = self.client.get("/api/improver/status", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["status"], "ACTIVE_UNATTENDED")
        self.assertGreaterEqual(data["total_unattended_ingests"], 1)
        self.assertGreaterEqual(data["total_optimizations_generated"], 1)
        self.assertIn("overall_knowledge_confidence_percent", data)
        self.assertTrue(len(data["learned_knowledge_items"]) >= 1)
        self.assertTrue(len(data["recent_pipeline_events"]) >= 1)

    def test_03_batch_relearning(self):
        """Tests reprocess_all_unattended method."""
        batch_res = continuous_improver.reprocess_all_unattended()
        self.assertEqual(batch_res["status"], "BATCH_COMPLETED")
        self.assertGreaterEqual(batch_res["processed_count"], 1)

    def test_04_trigger_relearning_endpoint(self):
        """Tests POST /api/improver/trigger-relearning endpoint."""
        resp = self.client.post("/api/improver/trigger-relearning", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "BATCH_RELEARNING_TRIGGERED")

if __name__ == "__main__":
    unittest.main()
