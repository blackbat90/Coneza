import sqlite3
import os

db_path = os.getenv("CONEZA_DB_PATH", "/srv/coneza-backend/backend/coneza_backend.db")
if not os.path.exists(db_path):
    db_path = "backend/coneza_backend.db"

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT id, username, role, must_change_password FROM users")
for row in c.fetchall():
    print(row)
