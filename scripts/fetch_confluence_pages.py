import json
import base64
import re
import urllib.request
import urllib.error
from html import unescape

with open('jira_config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

base_url = cfg['JIRA_URL'].rstrip('/')
auth_header = "Basic " + base64.b64encode(f"{cfg['JIRA_EMAIL']}:{cfg['JIRA_API_TOKEN']}".encode('utf-8')).decode('utf-8')

# Target key pages for Coneza product & technical ideas
target_page_titles = [
    "Requirements",
    "Architecture and Features",
    "Tech Functions",
    "Business Functions",
    "Development Strategy",
    "Potential EZA (SPS) suppliers",
    "Niederspannung",
    "Mittelspannung",
    "Hochspannung",
    "EMS",
    "Competitor analysis",
    "Customer Analysis",
    "EPC",
    "OEM"
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    # Remove HTML tags
    text = re.sub(r'<br\s*/?>', '\n', raw_html)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<li[^>]*>', '• ', text)
    text = re.sub(r'<h[1-6][^>]*>', '\n### ', text)
    text = re.sub(r'</h[1-6]>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    # Clean up excess whitespace
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(line for line in lines if line)

# Fetch all pages
req = urllib.request.Request(
    f"{base_url}/wiki/rest/api/content?limit=100&expand=body.storage,version",
    headers={"Authorization": auth_header, "Accept": "application/json"}
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    pages = data.get('results', [])

confluence_dump = {}

for p in pages:
    title = p.get('title')
    pid = p.get('id')
    body_storage = p.get('body', {}).get('storage', {}).get('value', '')
    clean_text = clean_html(body_storage)
    if clean_text:
        confluence_dump[title] = {
            "id": pid,
            "title": title,
            "content": clean_text
        }
        print(f"=== Extracted: {title} ({len(clean_text)} chars) ===")

with open('confluence_extracted_ideas.json', 'w', encoding='utf-8') as out_f:
    json.dump(confluence_dump, out_f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(confluence_dump)} pages to confluence_extracted_ideas.json")
