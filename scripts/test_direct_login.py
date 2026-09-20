import requests

url = "http://localhost:8080/api/auth/login"
resp = requests.post(url, json={"username": "engineer", "password": "EngineerSecure2026!"})
print("HTTP:", resp.status_code)
data = resp.json()
print("Status:", data.get("status"))
print("Must change password:", data.get("must_change_password"))
print("User:", data.get("user"))
