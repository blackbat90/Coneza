"""
Unit tests for the interactive plant questionnaire and digital SLD replacement (VDE-AR-N 4110).
"""

import unittest
import json
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db, get_connection
from backend.auth import create_access_token
from backend.component_catalog import get_full_catalog


class TestPlantQuestionnaire(unittest.TestCase):
    def setUp(self):
        init_db()
        from backend.main import seed_default_users
        seed_default_users()
        conn = get_connection()
        eng = conn.execute("SELECT id FROM users WHERE role = 'ENGINEER' OR username = 'engineer'").fetchone()
        user_id = eng[0] if eng else 1
        conn.close()
        self.client = TestClient(app)
        self.engineer_token = create_access_token(
            user_id=user_id, username="engineer", role="ENGINEER"
        )
        self.headers = {"Authorization": f"Bearer {self.engineer_token}"}

    def test_catalog_endpoint(self):
        """Tests that the catalog endpoint returns market standard components and presets."""
        res = self.client.get("/api/questionnaire/catalog", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("pv_inverters", data)
        self.assertIn("bess_systems", data)
        self.assertIn("transformers", data)
        self.assertIn("meters", data)
        self.assertIn("protection_relays", data)
        self.assertIn("presets", data)

        # Verify key brands exist
        pv_brands = [inv["brand"] for inv in data["pv_inverters"]]
        self.assertIn("Huawei", pv_brands)
        self.assertIn("SMA", pv_brands)
        self.assertIn("Sungrow", pv_brands)

        bess_brands = [b["brand"] for b in data["bess_systems"]]
        self.assertIn("BYD", bess_brands)
        self.assertIn("Tesla", bess_brands)

    def test_preview_sld_endpoint(self):
        """Tests live SVG generation and totals calculation without DB writes."""
        payload = {
            "plant_name": "Test Preview Solar Park",
            "grid_operator": "Netze BW GmbH (EnBW)",
            "voltage_level_kv": 20.0,
            "p_av_kw": 1200.0,
            "has_transformer": True,
            "transformer": {
                "rated_kva": 1600.0,
                "uk_percent": 6.0
            },
            "components": [
                {
                    "type": "PV_INVERTER",
                    "is_custom": False,
                    "brand": "Huawei",
                    "model": "SUN2000-115KTL-M2",
                    "count": 10,
                    "unit_active_kw": 115.0,
                    "unit_apparent_kva": 125.0
                }
            ],
            "meter": {"brand": "Janitza", "model": "UMG 604E"},
            "protection": {"brand": "Woodward", "model": "HighProTec MRM4"},
            "reactive_mode": "QU"
        }

        res = self.client.post("/api/questionnaire/preview-sld", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("totals", data)
        self.assertEqual(data["totals"]["p_inst_kw"], 1150.0)
        self.assertEqual(data["totals"]["s_inst_kva"], 1250.0)
        self.assertIn("<svg", data["svg"])
        self.assertIn("SUN2000-115KTL-M2", data["svg"])
        self.assertIn("Netze BW GmbH", data["svg"])

    def test_create_plant_with_market_components(self):
        """Tests creating a plant from questionnaire with market standard components."""
        payload = {
            "plant_name": "Solarpark EnBW Test 1.5MW",
            "grid_operator": "Netze BW GmbH (EnBW)",
            "voltage_level_kv": 20.0,
            "p_av_kw": 1500.0,
            "site_type": "PV",
            "has_transformer": True,
            "transformer": {
                "rated_kva": 1600.0,
                "uk_percent": 6.0
            },
            "components": [
                {
                    "type": "PV_INVERTER",
                    "is_custom": False,
                    "brand": "Huawei",
                    "model": "SUN2000-115KTL-M2",
                    "count": 13,
                    "unit_active_kw": 115.0,
                    "unit_apparent_kva": 125.0
                }
            ],
            "meter": {"brand": "Janitza", "model": "UMG 604E", "ip": "192.168.1.100"},
            "protection": {"brand": "Woodward", "model": "HighProTec MRM4"},
            "reactive_mode": "QU"
        }

        res = self.client.post("/api/plants/from-questionnaire", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        plant_id = data["plant_id"]
        doc_id_sld = data["doc_id_sld"]
        config_id = data["config_id"]

        self.assertTrue(plant_id.startswith("plant_"))
        self.assertTrue(doc_id_sld.startswith("doc_"))
        self.assertTrue(config_id.startswith("cfg_pcu_"))

        # Verify Plant in DB
        conn = get_connection()
        row = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["installed_capacity_kw"], 1495.0)

        # Verify Document (Digital SLD) in DB
        doc_row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id_sld,)).fetchone()
        self.assertIsNotNone(doc_row)
        self.assertEqual(doc_row["doc_type"], "SLD")
        ocr_data = json.loads(doc_row["ocr_data_json"])
        self.assertEqual(ocr_data["active_power_kw"], 1495.0)
        self.assertEqual(ocr_data["source"], "DIGITAL_QUESTIONNAIRE_SLD_REPLACEMENT")

        # Verify EZA Configuration in DB
        cfg_row = conn.execute("SELECT * FROM eza_configurations WHERE id = ?", (config_id,)).fetchone()
        self.assertIsNotNone(cfg_row)
        self.assertEqual(cfg_row["status"], "APPROVED")

        # Verify Modbus registers
        self.assertGreaterEqual(len(data["modbus_holding_registers"]), 35)
        conn.close()

    def test_create_plant_with_custom_components(self):
        """Tests defining custom inverters, custom BESS, and custom transformers."""
        payload = {
            "plant_name": "Custom Hybrid BESS 2MW",
            "grid_operator": "Bayernwerk Netz GmbH",
            "voltage_level_kv": 20.0,
            "p_av_kw": 2000.0,
            "site_type": "HYBRID",
            "has_transformer": True,
            "transformer": {
                "is_custom": True,
                "rated_kva": 2500.0,
                "uk_percent": 6.5,
                "vector_group": "Dyn11"
            },
            "components": [
                {
                    "type": "PV_INVERTER",
                    "is_custom": True,
                    "brand": "Spezial-Elektronik GmbH",
                    "model": "SolarPro-200X",
                    "count": 5,
                    "unit_active_kw": 200.0,
                    "unit_apparent_kva": 210.0
                },
                {
                    "type": "BESS",
                    "is_custom": True,
                    "brand": "HighEnergy Storage AG",
                    "model": "MegaStore-1000",
                    "count": 2,
                    "unit_active_kw": 500.0,
                    "unit_apparent_kva": 500.0,
                    "capacity_kwh": 1000.0
                }
            ],
            "meter": {"brand": "Siemens", "model": "PAC4200"},
            "protection": {"brand": "Ziehl", "model": "UFR1001E"},
            "reactive_mode": "COS_PHI"
        }

        res = self.client.post("/api/plants/from-questionnaire", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

        totals = data["totals"]
        # 5x 200 kW + 2x 500 kW = 2000 kW
        self.assertEqual(totals["p_inst_kw"], 2000.0)
        # 2x 1000 kWh = 2000 kWh
        self.assertEqual(totals["bess_capacity_kwh"], 2000.0)
        self.assertEqual(totals["trafo_kva"], 2500.0)

        # SVG contains custom names
        self.assertIn("Spezial-Elektronik GmbH", data["virtual_sld_svg"])
        self.assertIn("HighEnergy Storage AG", data["virtual_sld_svg"])
        self.assertIn("2000 kWh", data["virtual_sld_svg"])


if __name__ == "__main__":
    unittest.main()
