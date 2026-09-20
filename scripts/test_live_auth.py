import urllib.request
import urllib.error
import json
import ssl
import sys
import time
import os

# Import TOTP generation from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.totp_auth import get_totp_code

BASE_URL = "https://coneza.de/portal"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def api_post(endpoint, data, token=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_get(endpoint, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_patch(endpoint, data, token=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_delete(endpoint, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

print("=== 1. Testing Default Password Removal from UI ('Nicht Standart Passwort zeigen') ===")
req_html = urllib.request.Request(f"{BASE_URL}/", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req_html, context=ctx) as resp_html:
    html_content = resp_html.read().decode("utf-8")
assert "conezaAdmin2026!" not in html_content, "ERROR: Default password found in portal HTML!"
assert "engineer2026!" not in html_content, "ERROR: Default password found in portal HTML!"
print("[OK] Verified: No default passwords or hints appear in portal HTML source!")

print("\n=== 2. Testing Login & Forced Password Reset ('Passwort neusetzen erzwingen') ===")
# Try login with initial admin password or previously updated password
code, resp = api_post("/api/auth/login", {"username": "admin", "password": "conezaAdmin2026!"})
admin_token = None

if code == 200 and resp.get("status") == "PASSWORD_RESET_REQUIRED":
    print("[OK] Admin initial login correctly returned PASSWORD_RESET_REQUIRED!")
    temp_tok = resp["temp_token"]
    
    # Change password
    code_chg, resp_chg = api_post("/api/auth/change-password", {
        "temp_token": temp_tok,
        "old_password": "conezaAdmin2026!",
        "new_password": "liveAdminUpdatedSecret2026!"
    })
    print(f"Password reset response: Code {code_chg}, Status: {resp_chg.get('status')}")
    assert code_chg == 200 and resp_chg.get("status") == "success"
    admin_token = resp_chg["access_token"]
    print("[OK] Password successfully updated, obtained new admin access token!")
elif code == 200 and resp.get("access_token"):
    admin_token = resp["access_token"]
    print("[OK] Admin logged in with current password, access token acquired!")
else:
    # Try with updated password if already changed in previous run
    code_upd, resp_upd = api_post("/api/auth/login", {"username": "admin", "password": "liveAdminUpdatedSecret2026!"})
    if code_upd == 200 and resp_upd.get("status") == "PASSWORD_RESET_REQUIRED":
        code_chg, resp_chg = api_post("/api/auth/change-password", {
            "temp_token": resp_upd["temp_token"],
            "new_password": "conezaAdmin2026!"
        })
        admin_token = resp_chg["access_token"]
    elif code_upd == 200 and resp_upd.get("access_token"):
        admin_token = resp_upd["access_token"]
    else:
        raise RuntimeError(f"Could not authenticate admin: {code} / {resp} / {code_upd} / {resp_upd}")

assert admin_token is not None, "Failed to obtain admin token"

print("\n=== 3. Testing User Registration ===")
unique_user = f"user2fa_{int(time.time())}"
user_pw = "myStrongPassword2026!"
reg_payload = {
    "username": unique_user,
    "email": f"{unique_user}@coneza.de",
    "password": user_pw,
    "role": "ENGINEER"
}
code, reg_resp = api_post("/api/auth/register", reg_payload)
print(f"Registered user '{unique_user}': Code {code}, Role: {reg_resp.get('user', {}).get('role')}")
assert code == 200
user_token = reg_resp["access_token"]
test_user_id = reg_resp["user"]["id"]

print("\n=== 4. Testing 2FA Integration (TOTP RFC 6238) ===")
# 4a. 2FA Setup
code, setup_resp = api_get("/api/auth/2fa/setup", token=user_token)
print(f"2FA Setup -> Code {code}, Secret length: {len(setup_resp.get('secret', ''))}")
assert code == 200
totp_secret = setup_resp["secret"]
assert "otpauth://" in setup_resp["otpauth_url"]

# 4b. Verify & Enable 2FA with TOTP code
current_code = get_totp_code(totp_secret)
code, enable_resp = api_post("/api/auth/2fa/enable", {"totp_code": current_code}, token=user_token)
print(f"2FA Enable -> Code {code}, Message: {enable_resp.get('message')}")
assert code == 200 and enable_resp.get("status") == "success"

# 4c. Login challenge requires 2FA
code, login_resp = api_post("/api/auth/login", {"username": unique_user, "password": user_pw})
print(f"Login with 2FA active -> Code {code}, Status: {login_resp.get('status')}")
assert code == 200 and login_resp.get("status") == "2FA_REQUIRED"
temp_2fa_token = login_resp["temp_token"]

# 4d. Reject bad 2FA code
code, bad_verify = api_post("/api/auth/2fa/verify-login", {"temp_token": temp_2fa_token, "totp_code": "000000"})
print(f"Verify bad 2FA code -> Code {code} (Expect 400)")
assert code == 400

# 4e. Accept valid 2FA code
good_code = get_totp_code(totp_secret)
code, good_verify = api_post("/api/auth/2fa/verify-login", {"temp_token": temp_2fa_token, "totp_code": good_code})
print(f"Verify valid 2FA code -> Code {code}, Status: {good_verify.get('status')}, Token present: {'access_token' in good_verify}")
assert code == 200 and "access_token" in good_verify

print("\n=== 5. Testing Admin Forced Password Reset & 2FA Reset ===")
# 5a. Admin forces password reset on test user
code, force_resp = api_post(f"/api/auth/users/{test_user_id}/force-reset-password", {}, token=admin_token)
print(f"Admin force reset password -> Code {code}, Message: {force_resp.get('message')}")
assert code == 200

# 5b. Next login prompts for 2FA then requires password reset
code, login_after_force = api_post("/api/auth/login", {"username": unique_user, "password": user_pw})
assert login_after_force.get("status") == "2FA_REQUIRED"
code, verify_after_force = api_post("/api/auth/2fa/verify-login", {
    "temp_token": login_after_force["temp_token"],
    "totp_code": get_totp_code(totp_secret)
})
print(f"After 2FA on forced user -> Status: {verify_after_force.get('status')} (Expect PASSWORD_RESET_REQUIRED)")
assert verify_after_force.get("status") == "PASSWORD_RESET_REQUIRED"

# 5c. Admin resets 2FA for test user
code, reset_2fa_resp = api_post(f"/api/auth/users/{test_user_id}/reset-2fa", {}, token=admin_token)
print(f"Admin reset 2FA -> Code {code}, Message: {reset_2fa_resp.get('message')}")
assert code == 200

# 5d. Clean up test user
code, del_resp = api_delete(f"/api/auth/users/{test_user_id}", token=admin_token)
print(f"Admin delete test user -> Code {code}")
assert code == 200

print("\n=======================================================")
print("  ALL LIVE TESTS PASSED: 2FA + FORCED RESET + NO PW HINTS")
print("=======================================================")
