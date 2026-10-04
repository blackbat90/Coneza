import sqlite3

db_path = '/var/lib/docker/volumes/coneza_backend_data/_data/coneza_backend.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT id, username, email, role, must_change_password, is_2fa_enabled FROM users')
rows = cursor.fetchall()
print(f"Users found in {db_path}:")
for r in rows:
    print(r)
conn.close()
