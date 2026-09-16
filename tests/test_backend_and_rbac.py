"""
Test Suite for coneza Central Backend, RBAC, Multi-Device Fleet, and Gemini Analysis
"""

import os
import unittest
from fastapi.testclient import TestClient
from backend.main import app, seed_default_users
from backend.database import init_db

class TestBackendAndRBAC(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["CONEZA_DB_PATH"] = os.path.join(os.path.dirname(__file__), "test_backend.db")
        if os.path.exists(os.environ["CONEZA_DB_PATH"]):
            try:
                os.remove(os.environ["CONEZA_DB_PATH"])
            except Exception:
                pass
        init_db()
        seed_default_users()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(os.environ["CONEZA_DB_PATH"]):
            try:
                os.remove(os.environ["CONEZA_DB_PATH"])
            except Exception:
                pass

    def test_01_superuser_login(self):
        resp = self.client.post("/api/auth/login", json={"username": "admin", "password": "conezaAdmin2026!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "SUPER_ADMIN")
        TestBackendAndRBAC.super_token = data["access_token"]

    def test_02_engineer_login(self):
        resp = self.client.post("/api/auth/login", json={"username": "engineer", "password": "engineer2026!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["user"]["role"], "ENGINEER")
        TestBackendAndRBAC.engineer_token = data["access_token"]

    def test_03_viewer_login(self):
        resp = self.client.post("/api/auth/login", json={"username": "viewer", "password": "viewer2026!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["user"]["role"], "VIEWER")
        TestBackendAndRBAC.viewer_token = data["access_token"]

    def test_04_device_provision_rbac(self):
        payload = {
            "device_id": "coneza-edge-substation-bess-test",
            "name": "Substation BESS Edge",
            "local_ip": "192.168.10.45",
            "controller_host": "192.168.10.40",
            "controller_port": 5502
        }

        # Viewer should be forbidden (403)
        res_view = self.client.post("/api/devices/provision", json=payload, headers={"Authorization": f"Bearer {self.viewer_token}"})
        self.assertEqual(res_view.status_code, 403)

        # Super User should succeed (200)
        res_admin = self.client.post("/api/devices/provision", json=payload, headers={"Authorization": f"Bearer {self.super_token}"})
        self.assertEqual(res_admin.status_code, 200)

    def test_05_document_upload_and_ocr(self):
        samples_dir = os.path.join(os.path.dirname(__file__), "..", "samples")
        e8_path = os.path.join(samples_dir, "sample_E8_datasheet.pdf")
        
        with open(e8_path, "rb") as f:
            resp = self.client.post(
                "/api/documents/upload",
                files={"file": ("sample_E8_datasheet.pdf", f, "application/pdf")},
                data={"device_id": "coneza-edge-solar-park-01"}
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["detected_type"], "E8")
        TestBackendAndRBAC.uploaded_e8_id = data["id"]

    def test_06_gemini_analysis_and_eza_synthesis(self):
        # Trigger analysis
        resp = self.client.post(
            "/api/analysis/run",
            json={
                "device_id": "coneza-edge-solar-park-01",
                "document_ids": [self.uploaded_e8_id]
            },
            headers={"Authorization": f"Bearer {self.engineer_token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "COMPLETED")
        self.assertIn("analysis", data)
        self.assertIn("recommended_eza_config", data["analysis"])
        TestBackendAndRBAC.config_id = data["config_id"]

    def test_07_configuration_approval_and_deployment(self):
        # Viewer cannot approve (403)
        res_view = self.client.post(f"/api/configs/{self.config_id}/approve", headers={"Authorization": f"Bearer {self.viewer_token}"})
        self.assertEqual(res_view.status_code, 403)

        # Super User approves (200)
        res_approve = self.client.post(f"/api/configs/{self.config_id}/approve", headers={"Authorization": f"Bearer {self.super_token}"})
        self.assertEqual(res_approve.status_code, 200)

        # Super User deploys (200)
        res_deploy = self.client.post(
            "/api/configs/deploy",
            json={
                "config_id": self.config_id,
                "target_device_id": "coneza-edge-solar-park-01"
            },
            headers={"Authorization": f"Bearer {self.super_token}"}
        )
        self.assertEqual(res_deploy.status_code, 200)
        self.assertEqual(res_deploy.json()["status"], "QUEUED_FOR_DEPLOYMENT")

if __name__ == "__main__":
    unittest.main()
