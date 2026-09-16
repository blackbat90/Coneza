"""
Test Suite for Layout-Robust OCR & Grid Document Classification (E8, E9, SLD)
"""

import os
import unittest
from edge.ocr_engine import ocr_engine

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")

class TestGridDocumentOCR(unittest.TestCase):

    def test_e8_datasheet_extraction(self):
        file_path = os.path.join(SAMPLES_DIR, "sample_E8_datasheet.pdf")
        self.assertTrue(os.path.exists(file_path), f"Sample file not found: {file_path}")

        with open(file_path, "rb") as f:
            content = f.read()

        res = ocr_engine.extract_document(content, "sample_E8_datasheet.pdf")
        self.assertTrue(res["success"])
        self.assertEqual(res["detected_type"], "E8")
        entities = res["extracted_entities"]
        self.assertIn("active_power_kw", entities)
        self.assertEqual(entities["active_power_kw"], 2500.0)
        self.assertEqual(entities.get("grid_voltage_v"), 20000.0)
        self.assertEqual(entities.get("apparent_power_kva"), 2750.0)
        self.assertEqual(entities.get("transformer_uk_percent"), 6.0)

    def test_e9_commissioning_extraction(self):
        file_path = os.path.join(SAMPLES_DIR, "sample_E9_commissioning.pdf")
        self.assertTrue(os.path.exists(file_path), f"Sample file not found: {file_path}")

        with open(file_path, "rb") as f:
            content = f.read()

        res = ocr_engine.extract_document(content, "sample_E9_commissioning.pdf")
        self.assertTrue(res["success"])
        self.assertEqual(res["detected_type"], "E9")
        entities = res["extracted_entities"]
        self.assertEqual(entities.get("active_power_kw"), 2400.0)
        self.assertEqual(entities.get("reactive_mode"), "Q(U)")

    def test_sld_schematic_extraction(self):
        file_path = os.path.join(SAMPLES_DIR, "sample_SLD_schematic.pdf")
        self.assertTrue(os.path.exists(file_path), f"Sample file not found: {file_path}")

        with open(file_path, "rb") as f:
            content = f.read()

        res = ocr_engine.extract_document(content, "sample_SLD_schematic.pdf")
        self.assertTrue(res["success"])
        self.assertEqual(res["detected_type"], "SLD")
        entities = res["extracted_entities"]
        tags = entities.get("detected_equipment_tags", [])
        self.assertTrue(any(tag in tags for tag in ["Q0", "Q1", "T1"]))

if __name__ == "__main__":
    unittest.main()
