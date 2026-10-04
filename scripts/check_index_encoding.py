with open("backend/templates/index.html", "rb") as f:
    data = f.read()

has_crlf = b"\r\n" in data
print("Has CRLF:", has_crlf)
print("File length:", len(data))

target1 = b'<a href="${API_BASE}/api/documents/${doc.id}/download"'
print("Found target1:", target1 in data)
