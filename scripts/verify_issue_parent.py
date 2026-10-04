import urllib.request
import json
import base64

with open('jira_config.json', 'r') as f:
    cfg = json.load(f)

url = cfg['JIRA_URL'] + '/rest/api/3/issue/EEP-98'
auth = 'Basic ' + base64.b64encode(f"{cfg['JIRA_EMAIL']}:{cfg['JIRA_API_TOKEN']}".encode()).decode()

req = urllib.request.Request(url, headers={'Authorization': auth, 'Accept': 'application/json'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    parent = data.get('fields', {}).get('parent', {})
    print('ISSUE KEY:', data.get('key'))
    print('SUMMARY:', data.get('fields', {}).get('summary'))
    print('PARENT KEY:', parent.get('key'))
    print('PARENT SUMMARY:', parent.get('fields', {}).get('fields', {}).get('summary'))
