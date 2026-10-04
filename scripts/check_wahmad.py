import sqlite3

db_path = '/var/lib/docker/volumes/coneza_backend_data/_data/coneza_backend.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT id, username, email, hashed_password FROM users WHERE email LIKE "%coneza.de%"')
for r in cursor.fetchall():
    print(r[0], r[1], r[2])
conn.close()
