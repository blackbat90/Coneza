import sqlite3
import os

db_path = os.getenv("CONEZA_DB_PATH", "/data/coneza_backend.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Set must_change_password = 0 for admin and any existing users
cursor.execute("UPDATE users SET must_change_password = 0 WHERE username = 'admin'")
conn.commit()

cursor.execute("SELECT id, username, email, role, must_change_password, is_2fa_enabled FROM users")
for r in cursor.fetchall():
    print(r)

conn.close()
print("Successfully cleared must_change_password flag.")
