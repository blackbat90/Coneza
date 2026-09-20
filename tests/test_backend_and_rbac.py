"""
Test Suite for coneza Central Backend, RBAC, Multi-Device Fleet, and Gemini Analysis
"""

import os
import unittest
from fastapi.testclient import TestClient
from backend.main import app, seed_default_users
from backend.database import init_db
from backend.totp_auth import get_totp_code

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

    def test_01_superuser_login_and_forced_password_reset(self):
        # 1. First login of seeded admin returns PASSWORD_RESET_REQUIRED
        resp = self.client.post("/api/auth/login", json={"username": "admin", "password": "conezaAdmin2026!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "PASSWORD_RESET_REQUIRED")
        self.assertTrue(data["must_change_password"])
        temp_token = data["temp_token"]

        # 2. Cannot access protected API with temp token
        res_fail = self.client.get("/api/auth/users", headers={"Authorization": f"Bearer {temp_token}"})
        self.assertEqual(res_fail.status_code, 403)

        # 3. Change password to new secure password
        res_change = self.client.post("/api/auth/change-password", json={
            "temp_token": temp_token,
            "old_password": "conezaAdmin2026!",
            "new_password": "newSuperAdminPassword2026!"
        })
        self.assertEqual(res_change.status_code, 200)
        data_change = res_change.json()
        self.assertIn("access_token", data_change)
        self.assertEqual(data_change["user"]["role"], "SUPER_ADMIN")
        TestBackendAndRBAC.super_token = data_change["access_token"]

        # 4. Subsequent login succeeds directly
        res_direct = self.client.post("/api/auth/login", json={"username": "admin", "password": "newSuperAdminPassword2026!"})
        self.assertEqual(res_direct.status_code, 200)
        self.assertEqual(res_direct.json()["status"], "SUCCESS")

    def test_02_engineer_login(self):
        resp = self.client.post("/api/auth/login", json={"username": "engineer", "password": "engineer2026!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        if data.get("status") == "PASSWORD_RESET_REQUIRED":
            res_change = self.client.post("/api/auth/change-password", json={
                "temp_token": data["temp_token"],
                "new_password": "newEngineerPassword2026!"
            })
            self.assertEqual(res_change.status_code, 200)
            data = res_change.json()
        self.assertEqual(data["user"]["role"], "ENGINEER")
        TestBackendAndRBAC.engineer_token = data["access_token"]

    def test_03_viewer_login(self):
        resp = self.client.post("/api/auth/login", json={"username": "viewer", "password": "viewer2026!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        if data.get("status") == "PASSWORD_RESET_REQUIRED":
            res_change = self.client.post("/api/auth/change-password", json={
                "temp_token": data["temp_token"],
                "new_password": "newViewerPassword2026!"
            })
            self.assertEqual(res_change.status_code, 200)
            data = res_change.json()
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
        res_correct = self.client.post("/api/auth/login", json={"username": "admin", "password": "newSuperAdminPassword2026!"})
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

    def test_11_2fa_setup_and_login_flow(self):
        # 1. Setup 2FA
        res_setup = self.client.get("/api/auth/2fa/setup", headers={"Authorization": f"Bearer {self.engineer_token}"})
        self.assertEqual(res_setup.status_code, 200)
        data_setup = res_setup.json()
        self.assertIn("secret", data_setup)
        self.assertIn("otpauth_url", data_setup)
        secret = data_setup["secret"]

        # 2. Try activating with invalid code (400)
        res_bad_enable = self.client.post(
            "/api/auth/2fa/enable",
            json={"totp_code": "000000"},
            headers={"Authorization": f"Bearer {self.engineer_token}"}
        )
        self.assertEqual(res_bad_enable.status_code, 400)

        # 3. Activate with valid TOTP code (200)
        valid_code = get_totp_code(secret)
        res_enable = self.client.post(
            "/api/auth/2fa/enable",
            json={"totp_code": valid_code},
            headers={"Authorization": f"Bearer {self.engineer_token}"}
        )
        self.assertEqual(res_enable.status_code, 200)

        # 4. Next login requires 2FA challenge
        res_login_2fa = self.client.post("/api/auth/login", json={"username": "engineer", "password": "newEngineerPassword2026!"})
        self.assertEqual(res_login_2fa.status_code, 200)
        data_login_2fa = res_login_2fa.json()
        self.assertEqual(data_login_2fa["status"], "2FA_REQUIRED")
        temp_token = data_login_2fa["temp_token"]

        # 5. Invalid 2FA code rejected (400)
        res_verify_bad = self.client.post("/api/auth/2fa/verify-login", json={"temp_token": temp_token, "totp_code": "999999"})
        self.assertEqual(res_verify_bad.status_code, 400)

        # 6. Valid 2FA code completes login (200)
        valid_login_code = get_totp_code(secret)
        res_verify_good = self.client.post("/api/auth/2fa/verify-login", json={"temp_token": temp_token, "totp_code": valid_login_code})
        self.assertEqual(res_verify_good.status_code, 200)
        self.assertIn("access_token", res_verify_good.json())

    def test_12_admin_force_password_reset_and_reset_2fa(self):
        # Admin forces password reset for viewer
        res_force = self.client.post("/api/auth/users/3/force-reset-password", headers={"Authorization": f"Bearer {self.super_token}"})
        self.assertEqual(res_force.status_code, 200)

        # Viewer login now requires password reset
        res_v_login = self.client.post("/api/auth/login", json={"username": "viewer", "password": "newViewerPassword2026!"})
        self.assertEqual(res_v_login.status_code, 200)
        self.assertEqual(res_v_login.json()["status"], "PASSWORD_RESET_REQUIRED")

        # Admin resets 2FA for engineer (user 2)
        res_reset_2fa = self.client.post("/api/auth/users/2/reset-2fa", headers={"Authorization": f"Bearer {self.super_token}"})
        self.assertEqual(res_reset_2fa.status_code, 200)

if __name__ == "__main__":
    unittest.main()


