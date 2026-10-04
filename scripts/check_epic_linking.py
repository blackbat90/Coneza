import urllib.request
import urllib.parse
import json
import base64

with open('jira_config.json', 'r') as f:
    cfg = json.load(f)

url = cfg['JIRA_URL']
email = cfg['JIRA_EMAIL']
token = cfg['JIRA_API_TOKEN']
auth = 'Basic ' + base64.b64encode(f'{email}:{token}'.encode()).decode()

# Check issues in EEP that have EEP-94 as parent
jql = 'parent = EEP-94'
req = urllib.request.Request(f'{url}/rest/api/3/search?jql=' + urllib.parse.quote(jql), headers={'Authorization': auth, 'Accept': 'application/json'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print('Found issues with parent = EEP-94:', len(data.get('issues', [])))
        for iss in data.get('issues', [])[:3]:
            print(iss['key'], iss['fields']['summary'])
except Exception as e:
    print('Parent search error:', e)

# Also check createmetadata for Task issue type in EEP
req2 = urllib.request.Request(f'{url}/rest/api/3/issue/createmeta?projectKeys=EEP&expand=projects.issuetypes.fields', headers={'Authorization': auth, 'Accept': 'application/json'})
try:
    with urllib.request.urlopen(req2) as resp:
        meta = json.loads(resp.read().decode())
        for p in meta.get('projects', []):
            for it in p.get('issuetypes', []):
                if it['name'] in ['Task', 'Story']:
                    fields = it.get('fields', {})
                    has_parent = 'parent' in fields
                    epic_fields = [k for k, v in fields.items() if 'epic' in v.get('name', '').lower() or 'parent' in v.get('name', '').lower()]
                    print(f"Issue type {it['name']}: has_parent={has_parent}, epic_fields={epic_fields}")
except Exception as e:
    print('Create meta error:', e)
