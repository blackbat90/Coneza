from backend.database import get_db_path
import sqlite3

path = get_db_path()
print("Active DB path:", path)
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print("Tables:", tables)
if 'plants' in tables:
    c.execute("SELECT id, name, installed_capacity_kw FROM plants")
    print("Plants in DB:", c.fetchall())
else:
    print("No 'plants' table in", path)
conn.close()
