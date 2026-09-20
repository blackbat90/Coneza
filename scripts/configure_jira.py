import subprocess

API_TOKEN = 'ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7'

def run_remote(script: str):
    clean = script.replace('\r\n', '\n').strip() + '\n'
    p = subprocess.Popen(
        ['ssh', 'root@195.90.215.204', 'bash -s'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = p.communicate(input=clean)
    return out, err, p.returncode

def main():
    # 1. Update the docker-compose env file on server
    # The .env file is /srv/coneza-backend/docker/.env (next to docker-compose)
    # or we need to check if there's an .env in /srv/coneza-backend/
    script_check = """
ls /srv/coneza-backend/
ls /srv/coneza-backend/docker/ 2>/dev/null || true
cat /srv/coneza-backend/docker/.env 2>/dev/null || echo "no docker .env"
"""
    out, err, rc = run_remote(script_check)
    print("Server layout:", out)

    # 2. Write .env to the docker working dir
    env_content = f"""# ==============================================================================
# coneza Central Backend - Environment Configuration
# ==============================================================================

BACKEND_PORT=9080
GEMINI_API_KEY=
CONEZA_JWT_SECRET=coneza-super-secret-jwt-key-2026-vde4110

# Jira Integration (ai@coneza.de - Coneza AI Assistant)
JIRA_URL=https://easy-eza.atlassian.net
JIRA_EMAIL=ai@coneza.de
JIRA_API_TOKEN={API_TOKEN}
JIRA_PROJECT_KEY=EEP
JIRA_DEFAULT_ASSIGNEE_ID=712020:707b6fd3-3dc5-4970-9dc1-5edf85680ad5
JIRA_AI_ACCOUNT_ID=712020:dcb4ef61-1d65-4fa7-95f2-0afb471f0481
"""
    # Write env file on server
    write_script = f"""cat > /srv/coneza-backend/docker/.env << 'ENVEOF'
{env_content}
ENVEOF
echo "Written .env:"
cat /srv/coneza-backend/docker/.env | grep -v TOKEN | grep -v SECRET
"""
    out2, err2, rc2 = run_remote(write_script)
    print("Write result:", out2)
    if err2:
        print("ERR:", err2[:300])

    # 3. Update docker-compose to include Jira env vars
    # Read current compose file
    read_script = "cat /srv/coneza-backend/docker/docker-compose.backend.yml"
    out3, err3, rc3 = run_remote(read_script)
    print("Current compose:", out3[:500])

    # 4. Rebuild and restart using docker compose
    restart_script = """
cd /srv/coneza-backend/docker
docker compose -f docker-compose.backend.yml --env-file .env up -d --force-recreate coneza-backend
sleep 5
docker ps --filter name=coneza-backend-server --format "{{.Names}}: {{.Status}}"
"""
    out4, err4, rc4 = run_remote(restart_script)
    print("Restart:", out4)
    if err4:
        print("ERR:", err4[:300])

    # 5. Test the Jira API endpoint
    test_script = """
sleep 3
curl -s http://localhost:9080/api/jira/tickets
"""
    out5, err5, rc5 = run_remote(test_script)
    print("Jira endpoint test:", out5[:500])

if __name__ == '__main__':
    main()
