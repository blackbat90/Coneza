import unittest
import json
import os
import tempfile
from unittest.mock import patch
# Suppress local .env loading and API client initialization during import.
with patch.dict(os.environ, {"GEMINI_API_KEY": "", "OPENAI_API_KEY": ""}), patch("os.path.exists", return_value=False):
    from backend.hybrid_analyzer import HybridGridAnalyzer
from backend.database import init_db, get_connection

class TestHybridAnalyzer(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        env = patch.dict(os.environ, {"CONEZA_DB_PATH": os.path.join(temp.name, "test.db"), "GEMINI_API_KEY": "", "OPENAI_API_KEY": ""})
        env.start()
        self.addCleanup(env.stop)
        init_db()
        self.sample_docs = [
            {
                "id": "doc_e8_01",
                "filename": "E8_Datenblatt_Solarpark.pdf",
                "doc_type": "E8",
                "ocr_entities": {
                    "active_power_kw": 3000.0,
                    "grid_voltage_v": 20000.0,
                    "apparent_power_kva": 3150.0,
                    "transformer_uk_percent": 6.0
                },
                "full_text": "Formular E.8 Solarpark 3000 kW Nennleistung Mittelspannung 20 kV Trafo 3150 kVA"
            },
            {
                "id": "doc_e9_01",
                "filename": "E9_Netzbetreiber_Vorgaben.pdf",
                "doc_type": "E9",
                "ocr_entities": {
                    "active_power_kw": 2800.0,
                    "grid_voltage_v": 20000.0,
                    "reactive_mode": "Q(U)",
                    "cos_phi": 1.0
                },
                "full_text": "Formular E.9 Anschlussvorgabe P_AV = 2800 kW Blindleistungsmodus Q(U)"
            }
        ]

    def test_01_deterministic_rules_cross_audit(self):
        """Test analyzer without API keys executes deterministic VDE-AR-N 4110 engine without claiming verification or consensus."""
        analyzer = HybridGridAnalyzer(gemini_api_key=None, openai_api_key=None)
        result = analyzer.analyze_documents(self.sample_docs)

        self.assertIn("summary", result)
        self.assertIn("consensus_score", result)
        self.assertIsNone(result["consensus_score"])
        self.assertIn("cross_eval", result)
        self.assertEqual(result["cross_eval"]["status"], "REVIEW_REQUIRED")
        
        # Verify extracted parameters
        params = result["extracted_parameters"]
        self.assertEqual(params["installed_active_power_kw"], 3000.0)
        self.assertEqual(params["contracted_feed_in_limit_p_av_kw"], 2800.0)
        self.assertEqual(params["nominal_grid_voltage_kv"], 20.0)

        # Verify EZA controller config
        config = result["recommended_eza_config"]
        self.assertEqual(config, {})

    def test_02_consensus_arbitration_agreement(self):
        """Test mathematical consensus when both models agree on parameters."""
        analyzer = HybridGridAnalyzer(gemini_api_key=None, openai_api_key=None)

        analysis_gemini = {
            "extracted_parameters": {
                "nominal_grid_voltage_kv": 20.0,
                "installed_active_power_kw": 3000.0,
                "contracted_feed_in_limit_p_av_kw": 2800.0,
                "rated_apparent_power_kva": 3150.0,
                "transformer_rating_kva": 3150.0,
                "transformer_uk_percent": 6.0,
                "mandated_reactive_power_mode": "Q(U)"
            },
            "discrepancies": [],
            "recommended_eza_config": {"q_control_mode": 1}
        }

        analysis_openai = {
            "extracted_parameters": {
                "nominal_grid_voltage_kv": 20.0,
                "installed_active_power_kw": 3000.0,
                "contracted_feed_in_limit_p_av_kw": 2800.0,
                "rated_apparent_power_kva": 3150.0,
                "transformer_rating_kva": 3150.0,
                "transformer_uk_percent": 6.0,
                "mandated_reactive_power_mode": "Q(U)"
            },
            "discrepancies": [],
            "recommended_eza_config": {"q_control_mode": 1}
        }

        review_gemini = {
            "overall_score": 98,
            "verdict": "APPROVED",
            "critique_summary": "OpenAI parameter extraction fully aligns with VDE-AR-N 4110.",
            "parameter_audits": [],
            "safety_concerns": []
        }

        review_openai = {
            "overall_score": 98,
            "verdict": "APPROVED",
            "critique_summary": "Gemini parameter extraction is mathematically sound.",
            "parameter_audits": [],
            "safety_concerns": []
        }

        result = analyzer._synthesize_consensus(
            analysis_a=analysis_gemini,
            name_a="Gemini 3.7 Flash",
            analysis_b=analysis_openai,
            name_b="OpenAI GPT-4o",
            review_of_b_by_a=review_gemini,
            review_of_a_by_b=review_openai,
            documents=self.sample_docs
        )

        self.assertEqual(result["consensus_score"], 100.0)
        self.assertEqual(result["cross_eval"]["status"], "REVIEW_REQUIRED")
        self.assertEqual(len(result["cross_eval"]["parameter_comparisons"]), 7)
        for comp in result["cross_eval"]["parameter_comparisons"]:
            self.assertEqual(comp["status"], "CONFIRMED_BY_BOTH")

    def test_03_consensus_arbitration_with_dispute(self):
        """Test dispute detection when models diverge on transformer capacity."""
        analyzer = HybridGridAnalyzer(gemini_api_key=None, openai_api_key=None)

        analysis_gemini = {
            "extracted_parameters": {
                "nominal_grid_voltage_kv": 20.0,
                "installed_active_power_kw": 3000.0,
                "contracted_feed_in_limit_p_av_kw": 2800.0,
                "rated_apparent_power_kva": 3150.0,
                "transformer_rating_kva": 3150.0,
                "transformer_uk_percent": 6.0,
                "mandated_reactive_power_mode": "Q(U)"
            },
            "discrepancies": [],
            "recommended_eza_config": {"q_control_mode": 1}
        }

        analysis_openai = {
            "extracted_parameters": {
                "nominal_grid_voltage_kv": 20.0,
                "installed_active_power_kw": 3000.0,
                "contracted_feed_in_limit_p_av_kw": 2800.0,
                "rated_apparent_power_kva": 3150.0,
                "transformer_rating_kva": 2500.0,  # Intentional discrepancy
                "transformer_uk_percent": 6.0,
                "mandated_reactive_power_mode": "Q(U)"
            },
            "discrepancies": [],
            "recommended_eza_config": {"q_control_mode": 1}
        }

        review_gemini = {"overall_score": 80, "verdict": "WARNING", "critique_summary": "Disputed transformer rating."}
        review_openai = {"overall_score": 80, "verdict": "WARNING", "critique_summary": "Transformer bottleneck flagged."}

        result = analyzer._synthesize_consensus(
            analysis_a=analysis_gemini,
            name_a="Gemini 3.7 Flash",
            analysis_b=analysis_openai,
            name_b="OpenAI GPT-4o",
            review_of_b_by_a=review_gemini,
            review_of_a_by_b=review_openai,
            documents=self.sample_docs
        )

        # 6 out of 7 agree -> ~85.7%
        self.assertGreater(result["consensus_score"], 80.0)
        self.assertLess(result["consensus_score"], 100.0)

        # Disputed field should be flagged
        trafo_comp = next(c for c in result["cross_eval"]["parameter_comparisons"] if c["parameter"] == "transformer_rating_kva")
        self.assertEqual(trafo_comp["status"], "DISPUTED")
        # Conservative choice (min) was selected
        self.assertEqual(trafo_comp["agreed_value"], 2500.0)

    def test_04_db_schema_has_cross_eval_columns(self):
        """Verify database migration added cross_eval_json and consensus_score to analysis_jobs."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(analysis_jobs)")
        cols = [r[1] for r in cursor.fetchall()]
        conn.close()

        self.assertIn("cross_eval_json", cols)
        self.assertIn("consensus_score", cols)
        self.assertIn("models_used", cols)

if __name__ == "__main__":
    unittest.main()
