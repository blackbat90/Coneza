import subprocess
import glob
import os

print("1. Syncing backend files to server...")
# Sync all .py files in backend
for py_file in glob.glob("backend/*.py"):
    subprocess.run(["scp", "-o", "BatchMode=yes", py_file, f"root@195.90.215.204:/srv/coneza-backend/{py_file}"], check=True)

# Sync templates
subprocess.run(["scp", "-o", "BatchMode=yes", "backend/templates/index.html", "root@195.90.215.204:/srv/coneza-backend/backend/templates/index.html"], check=True)

# Sync static if exists
if os.path.exists("backend/static/pcu-draft.html"):
    subprocess.run(["scp", "-o", "BatchMode=yes", "backend/static/pcu-draft.html", "root@195.90.215.204:/srv/coneza-backend/backend/static/pcu-draft.html"], check=True)

remote_deploy = """
# Copy all backend files into running container
docker cp /srv/coneza-backend/backend/. coneza-backend-server:/app/backend/

# Restart backend container to load new code
docker restart coneza-backend-server

# Wait for container startup
sleep 4

# Check status and health
docker ps --filter "name=coneza-backend-server" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
curl -s http://localhost:9080/api/health
echo ""
"""

print("2. Applying updates to container and restarting...")
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", remote_deploy], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
