import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Test Health
req = urllib.request.Request("https://coneza.de/portal/api/health")
with urllib.request.urlopen(req, context=ctx) as r:
    print("Health:", r.read().decode())

# 2. Test Plants List
req = urllib.request.Request("https://coneza.de/portal/api/plants")
try:
    with urllib.request.urlopen(req, context=ctx) as r:
        plants = json.loads(r.read().decode())
        print(f"Plants count: {len(plants)}")
except Exception as e:
    print("Plants listing requires auth or returned:", e)
