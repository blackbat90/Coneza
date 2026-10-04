import json
import base64
import urllib.request
import urllib.error

with open('jira_config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

base_url = cfg['JIRA_URL'].rstrip('/')
auth_header = "Basic " + base64.b64encode(f"{cfg['JIRA_EMAIL']}:{cfg['JIRA_API_TOKEN']}".encode('utf-8')).decode('utf-8')

print(f"Connecting to Confluence at {base_url}/wiki/rest/api/...")

# 1. Test /wiki/rest/api/space
req = urllib.request.Request(
    f"{base_url}/wiki/rest/api/space",
    headers={"Authorization": auth_header, "Accept": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        results = data.get('results', [])
        print(f"Spaces found ({len(results)}):")
        for s in results:
            print(f" - [{s.get('key')}] {s.get('name')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')[:300]}")
except Exception as e:
    print(f"Error: {e}")

# 2. Test searching for content / pages
req_pages = urllib.request.Request(
    f"{base_url}/wiki/rest/api/content?limit=25&expand=body.storage,version",
    headers={"Authorization": auth_header, "Accept": "application/json"}
)

try:
    with urllib.request.urlopen(req_pages) as resp:
        pdata = json.loads(resp.read().decode('utf-8'))
        pages = pdata.get('results', [])
        print(f"\nPages found ({len(pages)}):")
        for p in pages:
            print(f" - ID: {p.get('id')} | Title: {p.get('title')} | Type: {p.get('type')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')[:300]}")
except Exception as e:
    print(f"Error fetching pages: {e}")
