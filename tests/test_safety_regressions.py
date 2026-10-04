"""Offline regressions: no application startup, credentials, sockets or real DB."""
import ast
import asyncio
import copy
import json
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend.configuration_safety import require_reviewable_configuration
from edge.phoenix_eza.controller import PhoenixEZAControllerClient


def load_analyzer():
    # Execute the actual class and standard-library imports, excluding .env and singleton.
    path = Path(__file__).resolve().parents[1] / "backend/hybrid_analyzer.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tree.body = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef))]
    namespace = {}
    exec(compile(tree, str(path), "exec"), namespace)
    return namespace["HybridGridAnalyzer"].__new__(namespace["HybridGridAnalyzer"])


class AnalysisSafetyTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = load_analyzer()
        self.params = dict(nominal_grid_voltage_kv=20, installed_active_power_kw=3000,
                           contracted_feed_in_limit_p_av_kw=2800, rated_apparent_power_kva=3150,
                           transformer_rating_kva=3150, transformer_uk_percent=6,
                           mandated_reactive_power_mode="Q(U)")
        self.analysis = {"extracted_parameters": self.params, "discrepancies": [],
                         "recommended_eza_config": {}}
        self.review = {"verdict": "APPROVED", "parameter_audits": [], "safety_concerns": []}
        self.docs = [{"full_text": "source data"}]
        # Obtain all required settings, then supply them explicitly in both candidates.
        draft = self.synthesize()
        self.analysis["recommended_eza_config"] = draft["recommended_eza_config"]

    def synthesize(self, other=None, review=None, docs=None):
        return self.analyzer._synthesize_consensus(
            self.analysis, "A", other or copy.deepcopy(self.analysis), "B",
            review or self.review, review or self.review, self.docs if docs is None else docs)

    def test_empty_and_partial_fallback_never_invents_plant_or_consensus(self):
        for docs in ([], [{"doc_type": "E8", "ocr_entities": {"active_power_kw": 0}}]):
            result = self.analyzer._deterministic_fallback_with_audit(docs)
            self.assertIsNone(result["consensus_score"])
            self.assertEqual(result["recommended_eza_config"], {})
            self.assertTrue(result["cross_eval"]["blocking_reasons"])
            self.assertNotIn("transformer_rating_kva", result["extracted_parameters"])
        self.assertEqual(result["extracted_parameters"]["installed_active_power_kw"], 0)

    def test_agreement_requires_human_review_not_certification(self):
        result = self.synthesize()
        self.assertEqual(result["consensus_score"], 100)
        self.assertEqual(result["cross_eval"]["status"], "READY_FOR_REVIEW")

    def test_critical_concern_and_changes_requested_override_full_consensus(self):
        for verdict, concerns in (("CHANGES_REQUESTED", []), ("APPROVED", [{"severity": "CRITICAL"}])):
            result = self.synthesize(review={"verdict": verdict, "safety_concerns": concerns})
            self.assertEqual(result["consensus_score"], 100)
            self.assertEqual(result["cross_eval"]["status"], "REVIEW_REQUIRED")

    def test_missing_disputed_and_defaulted_values_block(self):
        for kind in ("missing", "disputed", "config", "critical", "default"):
            other = copy.deepcopy(self.analysis)
            if kind == "missing":
                del other["extracted_parameters"]["transformer_rating_kva"]
            elif kind == "disputed":
                other["extracted_parameters"]["transformer_rating_kva"] = 2500
            elif kind == "config":
                other["recommended_eza_config"]["q_setpoint_kvar"] = -100
            elif kind == "critical":
                other["discrepancies"] = [{"severity": "CRITICAL"}]
            else:
                other["recommended_eza_config"] = {}
            self.assertEqual(self.synthesize(other)["cross_eval"]["status"], "REVIEW_REQUIRED", kind)
        self.assertEqual(self.synthesize(docs=[])["cross_eval"]["status"], "REVIEW_REQUIRED")

    def test_rules_do_not_confirm_missing_values(self):
        result = self.analyzer._rules_evaluate_analysis({}, {})
        self.assertNotEqual(result["verdict"], "APPROVED")
        self.assertTrue(all(a["status"] == "MISSING_DATA" for a in result["parameter_audits"]))


class ApprovalSafetyTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.addCleanup(self.conn.close)
        self.conn.executescript("""
            CREATE TABLE analysis_jobs (id TEXT, cross_eval_json TEXT, recommended_eza_config_json TEXT);
            CREATE TABLE eza_configurations (id TEXT, analysis_job_id TEXT, parameters_json TEXT, status TEXT);
            INSERT INTO analysis_jobs VALUES ('a', '{}', '{"p_setpoint_kw": 100}');
            INSERT INTO eza_configurations VALUES ('c', 'a', '{"p_setpoint_kw": 100}', 'DRAFT');
        """)

    def audit(self, value):
        self.conn.execute("UPDATE analysis_jobs SET cross_eval_json=?", (json.dumps(value),))

    def test_legacy_missing_or_blocked_audit_rejected_even_if_approved(self):
        self.conn.execute("UPDATE eza_configurations SET status='APPROVED'")
        for audit in ({}, {"status": "CERTIFIED"}, {"status": "REVIEW_REQUIRED"},
                      {"status": "READY_FOR_REVIEW", "blocking_reasons": ["critical"]}):
            self.audit(audit)
            with self.assertRaises(ValueError):
                require_reviewable_configuration(self.conn, "c", True)

    def test_approval_and_unchanged_parameters_required(self):
        self.audit({"status": "READY_FOR_REVIEW", "blocking_reasons": []})
        self.assertEqual(require_reviewable_configuration(self.conn, "c"), {"p_setpoint_kw": 100})
        with self.assertRaises(ValueError):
            require_reviewable_configuration(self.conn, "c", True)

        self.conn.execute("UPDATE eza_configurations SET status='APPROVED'")
        self.assertTrue(require_reviewable_configuration(self.conn, "c", True))
        self.conn.execute("UPDATE eza_configurations SET parameters_json='{}'")
        with self.assertRaises(ValueError):
            require_reviewable_configuration(self.conn, "c", True)

    def test_actual_api_endpoints_reject_before_update_or_queue(self):
        # Load real endpoint bodies without starting the app or its service singletons.
        path = Path(__file__).resolve().parents[1] / "backend/main.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tree.body = [n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                     and n.name in ("approve_configuration", "deploy_configuration")]
        for node in tree.body:
            node.decorator_list = []
            node.args.defaults = []
            for arg in node.args.args:
                arg.annotation = None
        connection = Mock(wraps=self.conn)
        connection.close = Mock()
        fleet = Mock()

        class Rejected(Exception):
            def __init__(self, status_code, detail):
                self.status_code = status_code

        namespace = dict(get_connection=lambda: connection, HTTPException=Rejected, fleet_manager=fleet)
        exec(compile(tree, str(path), "exec"), namespace)
        for name, value in (("approve_configuration", "c"),
                            ("deploy_configuration", Mock(config_id="c", target_device_id="d"))):
            with self.assertRaises(Rejected) as exc:
                asyncio.run(namespace[name](value, {"username": "test"}))
            self.assertEqual(exc.exception.status_code, 409)
        fleet.queue_configuration_deployment.assert_not_called()
        self.assertEqual(self.conn.execute("SELECT status FROM eza_configurations").fetchone()[0], "DRAFT")

    def test_queue_and_heartbeat_recheck_audit(self):
        from backend.device_manager import FleetDeviceManager
        manager = FleetDeviceManager()
        self.conn.execute("""CREATE TABLE devices (device_id TEXT, pending_config_json TEXT,
                          status TEXT, local_ip TEXT, controller_state TEXT, telemetry_json TEXT, last_heartbeat TEXT)""")
        pending = json.dumps({"job_id": "c", "parameters": {"p_setpoint_kw": 100}})
        self.conn.execute("INSERT INTO devices (device_id, pending_config_json) VALUES ('d', ?)", (pending,))
        self.conn.execute("UPDATE eza_configurations SET status='APPROVED'")
        self.conn.commit()
        connection = Mock(wraps=self.conn)
        connection.close = Mock()
        with patch("backend.device_manager.get_connection", return_value=connection):
            with self.assertRaises(ValueError):
                manager.queue_configuration_deployment("d", "c", {"p_setpoint_kw": 100})
            self.conn.rollback()
            self.assertIsNone(manager.process_heartbeat("d", {}))
            self.assertIsNone(self.conn.execute("SELECT pending_config_json FROM devices").fetchone()[0])
            self.audit({"status": "READY_FOR_REVIEW", "blocking_reasons": []})
            self.conn.commit()
            manager.queue_configuration_deployment("d", "c", {"p_setpoint_kw": 100})
            self.assertEqual(manager.process_heartbeat("d", {})["parameters"], {"p_setpoint_kw": 100})


class SignedConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_round_trip_all_q_points_and_signed_boundaries(self):
        client = PhoenixEZAControllerClient()
        registers = {}

        async def write(address, value):
            registers[address] = value & 0xffff

        async def read(address, count):
            return [registers.get(a, 0) for a in range(address, address + count)]

        with patch.object(client, "write_holding_register", side_effect=write), patch.object(
            client, "read_holding_registers", side_effect=read
        ), patch.object(client, "_execute_modbus_request", side_effect=AssertionError("Network forbidden")):
            for value in (-32768, -100, -1, 0, 1, 32767):
                config = {"q_setpoint_kvar": value, "q_u_curve": {
                    **{f"q{i}_percent": value / 10 for i in range(1, 5)},
                    **{f"u{i}_percent": 100 for i in range(1, 5)},
                }}
                await client.apply_configuration(config)
                actual = await client.read_active_configuration()
                self.assertEqual(actual["q_setpoint_kvar"], value)
                self.assertEqual(actual["q_u_curve"], config["q_u_curve"])
            await client.apply_configuration({"q_u_curve": {"q4_percent": -100}})
            self.assertEqual((await client.read_active_configuration())["q_u_curve"]["q4_percent"], -100)
