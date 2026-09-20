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

    def test_08_admin_requires_password(self):
        # Incorrect password must be rejected
        res_wrong = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrongPassword123!"})
        self.assertEqual(res_wrong.status_code, 401)
        self.assertIn("Invalid username or password", res_wrong.json()["detail"])

        # Correct password succeeds
        res_correct = self.client.post("/api/auth/login", json={"username": "admin", "password": "conezaAdmin2026!"})
        self.assertEqual(res_correct.status_code, 200)

    def test_09_user_registration(self):
        # Register new user
        reg_payload = {
            "username": "solar_engineer_new",
            "email": "solar.engineer@example.com",
            "password": "securePassword2026!",
            "role": "ENGINEER"
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 200)
        data = res_reg.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["username"], "solar_engineer_new")
        self.assertEqual(data["user"]["role"], "ENGINEER")
        TestBackendAndRBAC.new_user_id = data["user"]["id"]

        # Duplicate registration rejected
        res_dup = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_dup.status_code, 400)

    def test_10_user_management_rbac(self):
        # Viewer cannot list all users (403)
        res_view = self.client.get("/api/auth/users", headers={"Authorization": f"Bearer {self.viewer_token}"})
        self.assertEqual(res_view.status_code, 403)

        # Super admin can list users (200)
        res_admin = self.client.get("/api/auth/users", headers={"Authorization": f"Bearer {self.super_token}"})
        self.assertEqual(res_admin.status_code, 200)
        users = res_admin.json()
        self.assertTrue(len(users) >= 4)

        # Super admin can update user role
        res_role = self.client.patch(
            f"/api/auth/users/{self.new_user_id}/role",
            json={"role": "VIEWER"},
            headers={"Authorization": f"Bearer {self.super_token}"}
        )
        self.assertEqual(res_role.status_code, 200)
        self.assertEqual(res_role.json()["new_role"], "VIEWER")

        # Super admin can delete user
        res_del = self.client.delete(f"/api/auth/users/{self.new_user_id}", headers={"Authorization": f"Bearer {self.super_token}"})
        self.assertEqual(res_del.status_code, 200)

if __name__ == "__main__":
    unittest.main()

