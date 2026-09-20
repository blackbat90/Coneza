import urllib.request
import urllib.error
import ssl
import json
import base64

JIRA_URL = 'https://easy-eza.atlassian.net'
EMAIL = 'ai@coneza.de'
API_TOKEN = 'ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7'
PROJECT_KEY = 'EEP'
ASSIGNEE_ID = '712020:707b6fd3-3dc5-4970-9dc1-5edf85680ad5'  # Shehzad Saleem

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

def create_test_ticket():
    print("Creating test Jira ticket...")
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": "Jira-Integration erfolgreich eingerichtet - ai@coneza.de",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Die Jira-Integration wurde erfolgreich eingerichtet. Das KI-Konto ai@coneza.de ist jetzt mit dem Coneza-Portal verbunden und kann automatisch Tickets erstellen und Verbesserungen vorschlagen."
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Task"},
            "assignee": {"id": ASSIGNEE_ID}
        }
    }
    status, body = make_request(f'{JIRA_URL}/rest/api/3/issue', method='POST', data=payload)
    print(f"Status: {status}")
    if status == 201:
        key = body.get('key', 'N/A')
        url = f"{JIRA_URL}/browse/{key}"
        print(f"Created: {key}")
        print(f"URL: {url}")
        return key
    else:
        print(f"Error: {body}")
        return None

if __name__ == '__main__':
    create_test_ticket()
