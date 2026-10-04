import sqlite3

conn = sqlite3.connect("/data/coneza_backend.db")
cursor = conn.cursor()
users = cursor.execute("SELECT id, username, email, role FROM users").fetchall()
print("Portal Users in /data/coneza_backend.db:")
for u in users:
    print(u)
