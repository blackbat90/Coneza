import urllib.request
import urllib.error
import ssl
import re
import json

# The actual Atlassian signup/invite URL extracted from email tracking redirect
INVITE_URL = (
    'https://id.atlassian.com/signup/invite'
    '?signature=eyJraWQiOiJtaWNyb3MvYWlkLWFjY291bnQvcTAzOGE3Zzd1NTFmMGFpaiIsImFsZyI6IlJTMjU2In0'
    '.eyJzdWIiOiI3MTIwMjA6ZGNiNGVmNjEtMWQ2NS00ZmE3LTk1ZjItMGFmYjQ3MWYwNDgxIiwiYXVkIjoibGluay1zaWduYXR1cmUtdmFsaWRhdG9yIiwibmJmIjoxNzg5OTI5MTkxLCJzY29wZSI6Imludml0ZU90cCIsImluZm9Db2RlIjoiaW52aXRlZFVzZXIiLCJpc3MiOiJtaWNyb3MvYWlkLWFjY291bnQiLCJleHAiOjE3OTA1MzM5OTEsInVzZXJJZCI6IjcxMjAyMDpkY2I0ZWY2MS0xZDY1LTRmYTctOTVmMi0wYWZiNDcxZjA0ODEiLCJpYXQiOjE3ODk5MjkxOTEsImp0aSI6IjJhMzkwZTRmLTA0YmUtNGU1My1hMTA5LTZkMWIyOTRjMmE5OCJ9'
    '.DXed5QmXySDkGshtj8gx077Q8MEAlRcthqPtyK6fgli_u9mZWlYGxok9qPR-BMZLaPw2ZYtLg-w6fwCQezobgV1fdIngy0o8YHZF7r7Tg0P9MpiRX6L8hD1qVMd5wnjIYziXq4HXfbQSpWrXiNqT2xSnn0WyG9svWJ3w84oK0VK8iWZwoMn1tiZnP5j-FiCc3AHL0q3dSPCW5LSJq7p23SRsr6Tw8sL_iuud7ccS1bACL8sLlQcP7MTesbxjx5Zp8830Si1VTP24AMerFshzSbIs1i7jC9ZXphhcsQ0lKIV7tzqvOINocXSIeSoeg6-taZUhVFmwjlsawgD1Kxzntw'
    '&infoCode=invitedUser'
    '&atlOrigin=fab7687b408d4a70bafeaaa1c91581c0'
    '&continue=https%3A%2F%2Feasy-eza.atlassian.net%2Fjira%2Fland%3FatlOrigin%3Dfab7687b408d4a70bafeaaa1c91581c0'
    '&application=jira'
    '&flowTraceId=eaf13abe-df6e-4ff5-92b0-9fd06ffc8136'
)

print("=" * 60)
print("JIRA INVITATION ACCEPTANCE REQUIRED")
print("=" * 60)
print()
print("The Atlassian invitation for ai@coneza.de is ready.")
print("The signup URL requires JavaScript/browser interaction.")
print()
print("Please open this URL in your browser and accept the invitation:")
print()
print(INVITE_URL)
print()
print("Then set a password (suggest: C0nez@AI2026!) and complete the account setup.")
print()
print("After creating the account, please create an API token at:")
print("  https://id.atlassian.com/manage-profile/security/api-tokens")
print("  (Name it: Coneza Portal Agent)")
print()
print("Then add these to /srv/coneza-backend/.env on the server:")
print("  JIRA_URL=https://easy-eza.atlassian.net")
print("  JIRA_EMAIL=ai@coneza.de")
print("  JIRA_API_TOKEN=<your-api-token>")
print("  JIRA_PROJECT_KEY=<your-project-key>")
