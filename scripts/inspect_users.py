import sqlite3

conn = sqlite3.connect('/data/coneza_backend.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username, email, role, must_change_password, is_2fa_enabled FROM users')
rows = cursor.fetchall()
for r in rows:
    print(r)
conn.close()
