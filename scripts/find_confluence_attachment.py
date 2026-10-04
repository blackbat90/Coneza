import json
import base64
import urllib.request
import urllib.error

with open('jira_config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

base_url = cfg['JIRA_URL'].rstrip('/')
auth_header = 'Basic ' + base64.b64encode(f"{cfg['JIRA_EMAIL']}:{cfg['JIRA_API_TOKEN']}".encode('utf-8')).decode('utf-8')

# Search for attachments
url = f"{base_url}/wiki/rest/api/content?type=attachment&limit=100&expand=version,container,_links"
req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        results = data.get('results', [])
        print(f"Total attachments found: {len(results)}")
        for a in results:
            title = a.get('title')
            aid = a.get('id')
            container = a.get('container', {}).get('title')
            download_url = a.get('_links', {}).get('download')
            print(f"- {title} (ID: {aid}, Container: {container}, download: {download_url})")
except Exception as e:
    print("Error querying attachments:", e)

# Also search via CQL (Confluence Query Language) for VDE
cql_queries = [
    'text ~ "VDE*"',
    'title ~ "VDE*"',
    'type = "attachment"'
]
for q in cql_queries:
    encoded_q = urllib.parse.quote(q)
    cql_url = f"{base_url}/wiki/rest/api/content/search?cql={encoded_q}&limit=20"
    req_cql = urllib.request.Request(cql_url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req_cql) as resp:
            cql_data = json.loads(resp.read().decode('utf-8'))
            cql_results = cql_data.get('results', [])
            print(f"\nCQL '{q}' returned {len(cql_results)} items:")
            for item in cql_results:
                print(f"  * [{item.get('type')}] {item.get('title')} (ID: {item.get('id')})")
    except Exception as e:
        print(f"Error querying CQL '{q}':", e)
