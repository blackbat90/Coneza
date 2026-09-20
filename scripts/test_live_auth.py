import urllib.request
import urllib.error
import json
import ssl
import sys

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

print("=== 1. Testing Admin Password Requirement ===")
# 1a. Wrong password -> 401
code, resp = api_post("/api/auth/login", {"username": "admin", "password": "wrongPassword123!"})
print(f"Admin wrong password -> Code: {code}, Response: {resp}")
assert code == 401, f"Expected 401, got {code}"

# 1b. Correct password -> 200
code, resp = api_post("/api/auth/login", {"username": "admin", "password": "conezaAdmin2026!"})
print(f"Admin correct password -> Code: {code}, Token present: {'access_token' in resp}")
assert code == 200, f"Expected 200, got {code}"
admin_token = resp["access_token"]

print("\n=== 2. Testing User Registration ===")
import time
unique_user = f"live_reg_user_{int(time.time())}"
reg_payload = {
    "username": unique_user,
    "email": f"{unique_user}@coneza.de",
    "password": "strongPassword2026!",
    "role": "ENGINEER"
}
code, resp = api_post("/api/auth/register", reg_payload)
print(f"Register new user -> Code: {code}, Username: {resp.get('user', {}).get('username')}, Role: {resp.get('user', {}).get('role')}")
assert code == 200, f"Expected 200, got {code}"
new_user_id = resp["user"]["id"]
new_user_token = resp["access_token"]

# 2b. Attempt duplicate registration -> 400
code_dup, resp_dup = api_post("/api/auth/register", reg_payload)
print(f"Register duplicate user -> Code: {code_dup}, Detail: {resp_dup}")
assert code_dup == 400, f"Expected 400, got {code_dup}"

print("\n=== 3. Testing Login for Newly Registered User ===")
code, resp = api_post("/api/auth/login", {"username": unique_user, "password": "strongPassword2026!"})
print(f"Login new user -> Code: {code}, Token present: {'access_token' in resp}")
assert code == 200, f"Expected 200, got {code}"

print("\n=== 4. Testing User Management (Admin Only) ===")
# 4a. Viewer / non-admin cannot list users
code, resp = api_get("/api/auth/users", token=new_user_token)
print(f"Non-admin listing users -> Code: {code} (Expect 403)")
assert code == 403, f"Expected 403, got {code}"

# 4b. Admin can list users
code, users = api_get("/api/auth/users", token=admin_token)
print(f"Admin listing users -> Code: {code}, Total users: {len(users)}")
assert code == 200, f"Expected 200, got {code}"
assert any(u["username"] == unique_user for u in users)

# 4c. Admin can change user role
code, resp = api_patch(f"/api/auth/users/{new_user_id}/role", {"role": "VIEWER"}, token=admin_token)
print(f"Admin change user role -> Code: {code}, Result: {resp}")
assert code == 200, f"Expected 200, got {code}"
assert resp["new_role"] == "VIEWER"

# 4d. Admin can delete user
code, resp = api_delete(f"/api/auth/users/{new_user_id}", token=admin_token)
print(f"Admin delete user -> Code: {code}, Result: {resp}")
assert code == 200, f"Expected 200, got {code}"

print("\n=== ALL LIVE TESTS PASSED SUCCESSFULLY! ===")
