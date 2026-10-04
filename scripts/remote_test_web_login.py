
import requests
import re

session = requests.Session()
# 1. GET login page to get CSRF token and session cookie
r = session.get('https://127.0.0.1:8443/', verify=False)
csrf = re.search(r'name="csrf_token"\s+value="([a-f0-9]+)"', r.text)
if not csrf:
    csrf = re.search(r'value="([a-f0-9]{64})".*?csrf_token', r.text)
token = csrf.group(1) if csrf else None
print("CSRF Token:", token)

# 2. POST login
data = {
    'login_user': 's.saleem@coneza.de',
    'pass_user': 'ConezaSecure2026!',
    'csrf_token': token
}
r2 = session.post('https://127.0.0.1:8443/', data=data, verify=False)
print("Login status code:", r2.status_code)
print("Login cookies:", session.cookies.get_dict())
if 'logged_in_as' in r2.text or 's.saleem@coneza.de' in r2.text or 'logout' in r2.text:
    print("SUCCESS: Logged in successfully!")
else:
    print("Login response text snippet:", r2.text[:400])
