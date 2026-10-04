import subprocess

test_prod_script = """
import requests

BASE = "http://localhost:9080"

# 1. Login
login_res = requests.post(f"{BASE}/api/auth/login", json={
    "username": "s.saleem@coneza.de",
    "password": "ConezaSecure2026!"
})
print("Login status:", login_res.status_code)
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Upload real sample PDF
with open("/srv/coneza-backend/samples/sample_SLD_schematic.pdf", "rb") as f:
    pdf_data = f.read()

files = {"file": ("sample_SLD_schematic.pdf", pdf_data, "application/pdf")}
upload_res = requests.post(f"{BASE}/api/documents/upload", files=files, data={"doc_type": "SLD"}, headers=headers)
print("Upload status:", upload_res.status_code)
assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
doc_id = upload_res.json()["id"]
print(f"Created test document: {doc_id}")

# 3. Verify document exists in list
docs_res = requests.get(f"{BASE}/api/documents", headers=headers)
assert docs_res.status_code == 200
docs = docs_res.json()
assert any(d["id"] == doc_id for d in docs), "Uploaded document not in list"
print("Document confirmed in list!")

# 4. Delete document
del_res = requests.delete(f"{BASE}/api/documents/{doc_id}", headers=headers)
print("Delete status:", del_res.status_code)
print("Delete response:", del_res.json())
assert del_res.status_code == 200, f"Delete failed: {del_res.text}"

# 5. Verify document is deleted
docs_res_after = requests.get(f"{BASE}/api/documents", headers=headers)
assert not any(d["id"] == doc_id for d in docs_res_after.json()), "Document still in list after deletion"

down_res = requests.get(f"{BASE}/api/documents/{doc_id}/download", headers=headers)
assert down_res.status_code == 404, "Download endpoint did not return 404"

print("PROD VERIFICATION COMPLETE: Document deletion is working 100% on production!")
"""

with open("c:/Workplace/Coneza/Coneza/scripts/remote_test_doc_delete.py", "w") as f:
    f.write(test_prod_script)

subprocess.run(["scp", "-o", "BatchMode=yes", "c:/Workplace/Coneza/Coneza/scripts/remote_test_doc_delete.py", "root@195.90.215.204:/tmp/test_doc_del.py"], check=True)
res = subprocess.run(["ssh", "-o", "BatchMode=yes", "root@195.90.215.204", "python3 /tmp/test_doc_del.py"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
