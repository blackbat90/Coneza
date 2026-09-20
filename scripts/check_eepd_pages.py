import urllib.request
import urllib.error
import json
import base64
import ssl

JIRA_URL = "https://easy-eza.atlassian.net"
EMAIL = "ai@coneza.de"
API_TOKEN = "ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7"

auth_str = f"{EMAIL}:{API_TOKEN}"
b64_auth = base64.b64encode(auth_str.encode("ascii")).decode("ascii")

headers = {
    "Authorization": f"Basic {b64_auth}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

ctx = ssl.create_default_context()

print("--- Checking Pages in Space EEPD ---")
url = f"{JIRA_URL}/wiki/rest/api/content?spaceKey=EEPD&limit=25&expand=version,body.storage"
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode("utf-8"))
        results = data.get("results", [])
        print(f"Status: {response.status}, Pages found: {len(results)}")
        for page in results:
            print(f"- ID: {page.get('id')}, Title: {page.get('title')}, Status: {page.get('status')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
