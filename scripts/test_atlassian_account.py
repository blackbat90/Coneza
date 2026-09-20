import urllib.request
import urllib.error
import ssl
import json
import base64

EMAIL = 'ai@coneza.de'
API_TOKEN = 'ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7'
JIRA_URL = 'https://easy-eza.atlassian.net'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def make_request(url, method='GET', data=None):
    creds = base64.b64encode(f'{EMAIL}:{API_TOKEN}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {creds}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        body = resp.read().decode('utf-8')
        return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'raw': body[:500]}

def main():
    print("=== Testing Atlassian API Token ===")

    # 1. Test authentication
    status, body = make_request(f'{JIRA_URL}/rest/api/3/myself')
    print(f"\n1. Auth check: {status}")
    if status == 200:
        account_id = body.get('accountId', '')
        print(f"   Account ID: {account_id}")
        print(f"   Name: {body.get('displayName')}")
        print(f"   Email: {body.get('emailAddress')}")
        print(f"   Active: {body.get('active')}")

        # 2. List projects
        status2, body2 = make_request(f'{JIRA_URL}/rest/api/3/project')
        print(f"\n2. Projects: {status2}")
        projects = []
        if status2 == 200:
            projects = body2 if isinstance(body2, list) else body2.get('values', [])
            for p in projects:
                print(f"   - {p.get('key')}: {p.get('name')}")

        # 3. Get users/assignees in the project (find admin user ID)
        print(f"\n3. Users who can be assigned:")
        status3, body3 = make_request(f'{JIRA_URL}/rest/api/3/users/search?query=shehzad&maxResults=5')
        assignee_id = ''
        if status3 == 200:
            for u in body3:
                print(f"   - {u.get('displayName')} | ID: {u.get('accountId')} | Email: {u.get('emailAddress', 'N/A')}")
                if 'shehzad' in u.get('displayName', '').lower() or 's.saleem' in u.get('emailAddress', '').lower():
                    assignee_id = u.get('accountId', '')
        
        # Save config
        project_key = projects[0].get('key', 'CONEZA') if projects else 'CONEZA'
        config = {
            'JIRA_URL': JIRA_URL,
            'JIRA_EMAIL': EMAIL,
            'JIRA_API_TOKEN': API_TOKEN,
            'JIRA_PROJECT_KEY': project_key,
            'JIRA_DEFAULT_ASSIGNEE_ID': assignee_id,
            'AI_ACCOUNT_ID': account_id,
        }
        
        with open('jira_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Config saved to jira_config.json")
        print(f"   Project Key: {project_key}")
        print(f"   Assignee ID: {assignee_id}")
    else:
        print(f"   ERROR: {body}")

if __name__ == '__main__':
    main()
