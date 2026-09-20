import sqlite3
import os
import bcrypt

db_path = os.getenv("CONEZA_DB_PATH", "/data/coneza_backend.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT id, username, hashed_password, must_change_password FROM users WHERE username = 'admin'")
row = c.fetchone()
print("Admin row:", row[0], row[1], row[3])
pw_hash = row[2]

passwords_to_try = [
    "conezaAdmin2026!",
    "newSuperAdminPassword2026!",
    "liveAdminUpdatedSecret2026!"
]
for p in passwords_to_try:
    match = bcrypt.checkpw(p.encode("utf-8"), pw_hash.encode("utf-8"))
    print(f"Password '{p}': {match}")
