"""
Comprehensive Unit Tests for Confluence Integration, VNB TAB-Preset Engine,
Multi-EZE Dispatch Priority Logic, and Local Edge Store-and-Forward Buffer.
"""

import os
import json
import unittest
from fastapi.testclient import TestClient

from backend.main import app, seed_default_users
from backend.database import init_db, get_connection
from backend.auth import create_access_token
from backend.confluence_service import confluence_service
from backend.tab_presets import tab_preset_engine, VNB_TAB_PRESETS
from edge.dispatch_engine import dispatch_engine, DispatchRequest, GenerationUnit
from edge.local_buffer import LocalStoreAndForwardBuffer
from backend.confluence_task_ai import confluence_task_ai


class TestConfluenceAndTabEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db = os.path.join(os.path.dirname(__file__), "test_confluence_suite.db")
        os.environ["CONEZA_DB_PATH"] = cls.test_db
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass
        init_db()
        seed_default_users()
        cls.client = TestClient(app)
        cls.token = create_access_token(user_id=1, username="admin", role="SUPER_ADMIN")
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass

    def test_01_confluence_service_and_summary(self):
        """Verify Confluence service extracts clean text and requirements summary."""
        summary = confluence_service.get_key_requirements_summary()
        self.assertIn("total_pages", summary)
        self.assertIn("architecture_features", summary)
        self.assertIn("edge_cases", summary)
        self.assertTrue(summary["has_dso_database"])

    def test_02_vnb_tab_presets_listing(self):
        """Verify German DSOs (Bayernwerk, Netze BW, Westnetz, E.DIS, Mitnetz) are available."""
        presets = tab_preset_engine.list_presets()
        self.assertGreaterEqual(len(presets), 6)
        dso_ids = [p["dso_id"] for p in presets]
        self.assertIn("bayernwerk", dso_ids)
        self.assertIn("netze_bw", dso_ids)
        self.assertIn("westnetz", dso_ids)
        self.assertIn("edis", dso_ids)
        self.assertIn("mitnetz", dso_ids)

        # Verify Bayernwerk Q(U) settings
        bayern = tab_preset_engine.get_preset("bayernwerk")
        self.assertIsNotNone(bayern)
        self.assertEqual(bayern.q_u_curve["u2_percent"], 97.0)
        self.assertEqual(bayern.q_u_curve["u3_percent"], 103.0)

    def test_03_apply_vnb_tab_preset_to_config(self):
        """Verify applying a DSO TAB preset merges parameters into configuration."""
        base_cfg = {
            "rated_active_power_kw": 2500,
            "p_max_feed_in_limit_kw": 2400,
            "q_control_mode": 0
        }
        updated = tab_preset_engine.apply_preset_to_config(base_cfg, "netze_bw")
        self.assertEqual(updated["q_control_mode"], 1)
        self.assertEqual(updated["dso_id"], "netze_bw")
        self.assertIn("Netze BW GmbH", updated["dso_name"])
        self.assertEqual(updated["protection"]["u_max_percent"], 115.0)

    def test_04_multi_eze_dispatch_priority_bess_absorbs_all(self):
        """Test Confluence Requirement: BESS absorbs curtailed excess power before PV is throttled."""
        req = DispatchRequest(
            total_plant_capacity_kw=2000.0,
            curtailment_target_percent=70.0,  # Max 1400 kW allowed feed-in
            units=[
                GenerationUnit(
                    unit_id="inv-pv-01",
                    unit_type="PV_INVERTER",
                    rated_power_kw=1000.0,
                    current_power_kw=900.0
                ),
                GenerationUnit(
                    unit_id="inv-pv-02",
                    unit_type="PV_INVERTER",
                    rated_power_kw=1000.0,
                    current_power_kw=800.0
                ),
                GenerationUnit(
                    unit_id="bess-01",
                    unit_type="BESS",
                    rated_power_kw=500.0,
                    current_power_kw=0.0,
                    soc_percent=45.0,  # Ample room to charge
                    max_charge_power_kw=400.0
                )
            ]
        )
        # Total PV = 1700 kW. Allowed = 1400 kW. Excess = 300 kW.
        # BESS can absorb up to 400 kW -> absorbs full 300 kW!
        result = dispatch_engine.calculate_dispatch(req)
        self.assertEqual(result.compliance_status, "COMPLIANT")
        self.assertEqual(result.curtailed_loss_prevented_by_bess_kw, 300.0)
        self.assertEqual(result.total_feed_in_kw, 1400.0)

        # Inverters should NOT be curtailed because battery absorbed all excess
        bess_setpoint = next(s for s in result.unit_setpoints if s.unit_id == "bess-01")
        self.assertEqual(bess_setpoint.bess_charging_kw, 300.0)
        self.assertEqual(bess_setpoint.target_power_kw, -300.0)

    def test_05_multi_eze_dispatch_bess_full_inverters_curtailed(self):
        """Test BESS at 96% SoC cannot absorb -> Inverters are curtailed proportionally."""
        req = DispatchRequest(
            total_plant_capacity_kw=2000.0,
            curtailment_target_percent=50.0,  # Max 1000 kW allowed feed-in
            units=[
                GenerationUnit(
                    unit_id="inv-pv-01",
                    unit_type="PV_INVERTER",
                    rated_power_kw=1000.0,
                    current_power_kw=800.0
                ),
                GenerationUnit(
                    unit_id="inv-pv-02",
                    unit_type="PV_INVERTER",
                    rated_power_kw=1000.0,
                    current_power_kw=800.0
                ),
                GenerationUnit(
                    unit_id="bess-01",
                    unit_type="BESS",
                    rated_power_kw=500.0,
                    current_power_kw=0.0,
                    soc_percent=98.0  # Full battery, cannot charge
                )
            ]
        )
        result = dispatch_engine.calculate_dispatch(req)
        self.assertEqual(result.compliance_status, "COMPLIANT")
        self.assertEqual(result.curtailed_loss_prevented_by_bess_kw, 0.0)
        self.assertEqual(result.total_feed_in_kw, 1000.0)

        # Both inverters curtailed proportionally from 800 kW to 500 kW
        for sp in result.unit_setpoints:
            if sp.unit_type == "PV_INVERTER":
                self.assertEqual(sp.target_power_kw, 500.0)
                self.assertEqual(sp.target_power_percent, 50.0)

    def test_06_edge_local_store_and_forward_buffer(self):
        """Test local SQLite buffering and sync lifecycle for offline edge scenarios."""
        buf_db = os.path.join(os.path.dirname(__file__), "test_edge_buffer.db")
        if os.path.exists(buf_db):
            try:
                os.remove(buf_db)
            except Exception:
                pass

        buf = LocalStoreAndForwardBuffer(buf_db)
        # Buffer 3 records while offline
        rec1 = buf.buffer_record("dev-01", {"p_act": 2400, "q_act": 15})
        rec2 = buf.buffer_record("dev-01", {"p_act": 2420, "q_act": 18})
        rec3 = buf.buffer_record("dev-02", {"p_act": 1100, "q_act": -5})

        stats = buf.get_buffer_stats()
        self.assertEqual(stats["pending_offline_records"], 3)
        self.assertEqual(stats["synced_records"], 0)

        # Read pending
        pending = buf.get_pending_records(limit=10)
        self.assertEqual(len(pending), 3)

        # Mark 2 as synced
        buf.mark_records_synced([rec1, rec2])
        stats_after = buf.get_buffer_stats()
        self.assertEqual(stats_after["pending_offline_records"], 1)
        self.assertEqual(stats_after["synced_records"], 2)

        # Clean up
        if os.path.exists(buf_db):
            try:
                os.remove(buf_db)
            except Exception:
                pass

    def test_07_confluence_ai_task_synthesizer(self):
        """Test AI task synthesis generates structured tasks and ChatGPT prompts."""
        res = confluence_task_ai.generate_tasks_from_confluence()
        self.assertGreaterEqual(len(res.generated_tasks), 3)
        self.assertIn("ChatGPT", res.chatgpt_copy_prompt)
        titles = [t.title for t in res.generated_tasks]
        self.assertTrue(any("VNB TAB" in t or "TAB" in t for t in titles))
        self.assertTrue(any("Dispatch" in t or "BESS" in t for t in titles))

    def test_08_api_endpoints_tab_and_dispatch(self):
        """Test FastAPI endpoints for TAB presets, dispatch calculation, and Confluence requirements."""
        # 1. GET /api/tab/presets
        resp_presets = self.client.get("/api/tab/presets", headers=self.headers)
        self.assertEqual(resp_presets.status_code, 200)
        presets_json = resp_presets.json()
        self.assertIsInstance(presets_json, list)
        self.assertGreaterEqual(len(presets_json), 5)

        # 2. GET /api/confluence/requirements
        resp_reqs = self.client.get("/api/confluence/requirements", headers=self.headers)
        self.assertEqual(resp_reqs.status_code, 200)
        reqs_json = resp_reqs.json()
        self.assertIn("architecture_features", reqs_json)

        # 3. POST /api/dispatch/calculate
        disp_payload = {
            "total_plant_capacity_kw": 1000.0,
            "curtailment_target_percent": 80.0,
            "units": [
                {
                    "unit_id": "pv-1",
                    "unit_type": "PV_INVERTER",
                    "rated_power_kw": 1000.0,
                    "current_power_kw": 900.0
                }
            ]
        }
        resp_disp = self.client.post("/api/dispatch/calculate", json=disp_payload, headers=self.headers)
        self.assertEqual(resp_disp.status_code, 200)
        disp_res = resp_disp.json()
        self.assertEqual(disp_res["allowed_feed_in_kw"], 800.0)
        self.assertEqual(disp_res["compliance_status"], "COMPLIANT")

        # 4. POST /api/confluence/generate-tasks
        resp_tasks = self.client.post("/api/confluence/generate-tasks", headers=self.headers)
        self.assertEqual(resp_tasks.status_code, 200)
        tasks_json = resp_tasks.json()
        self.assertIn("generated_tasks", tasks_json)
        self.assertGreaterEqual(len(tasks_json["generated_tasks"]), 3)


if __name__ == "__main__":
    unittest.main()
