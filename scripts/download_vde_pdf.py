import json
import base64
import urllib.request
import os
import time

with open('jira_config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

base_url = cfg['JIRA_URL'].rstrip('/')
auth_header = 'Basic ' + base64.b64encode(f"{cfg['JIRA_EMAIL']}:{cfg['JIRA_API_TOKEN']}".encode('utf-8')).decode('utf-8')

att_id = "1703937"
full_download_url = base_url + "/wiki/rest/api/content/1671169/child/attachment/att1703937/download"
out_pdf = "VDE_AR_N_4110_2023.pdf"

print("Downloading from:", full_download_url)
req = urllib.request.Request(full_download_url, headers={'Authorization': auth_header})

max_retries = 3
for attempt in range(max_retries):
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(out_pdf, 'wb') as f_out:
            total_read = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f_out.write(chunk)
                total_read += len(chunk)
                if total_read % (1024 * 1024 * 5) == 0:
                    print(f"Read {total_read / (1024*1024):.1f} MB...")
            print(f"Successfully downloaded {total_read} bytes ({total_read / (1024*1024):.2f} MB) to {out_pdf}")
            break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(2)
