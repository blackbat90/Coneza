import urllib.request
import json
import base64

with open('jira_config.json', 'r') as f:
    cfg = json.load(f)

url = cfg['JIRA_URL']
email = cfg['JIRA_EMAIL']
token = cfg['JIRA_API_TOKEN']
auth = 'Basic ' + base64.b64encode(f'{email}:{token}'.encode()).decode()

fields = {
    'project': {'key': 'EEP'},
    'summary': '[AI Test] Epic Link Validation EEP-94',
    'description': {
        'type': 'doc',
        'version': 1,
        'content': [{
            'type': 'paragraph',
            'content': [{'type': 'text', 'text': 'Testing parent epic assignment to EEP-94.'}]
        }]
    },
    'issuetype': {'name': 'Task'},
    'parent': {'key': 'EEP-94'},
    'labels': ['ai-generated', 'coneza-portal', 'epic-eep-94']
}

req = urllib.request.Request(
    f'{url}/rest/api/3/issue',
    data=json.dumps({'fields': fields}).encode('utf-8'),
    headers={'Authorization': auth, 'Content-Type': 'application/json', 'Accept': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        created_key = res['key']
        print('SUCCESS! Created issue:', created_key)
        
        # Verify parent
        req_chk = urllib.request.Request(f'{url}/rest/api/3/issue/{created_key}?fields=summary,parent,issuetype', headers={'Authorization': auth, 'Accept': 'application/json'})
        with urllib.request.urlopen(req_chk) as r_chk:
            chk = json.loads(r_chk.read().decode('utf-8'))
            parent_key = chk['fields'].get('parent', {}).get('key')
            parent_summary = chk['fields'].get('parent', {}).get('fields', {}).get('summary')
            print(f'Verified Parent: {parent_key} ({parent_summary})')
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)
