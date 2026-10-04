import sys, os
sys.path.insert(0, os.path.abspath('.'))
from backend.database import get_connection, init_db
init_db()
con = get_connection()
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('DB Tables:', tables)
for t in ['plants', 'devices', 'documents', 'eza_configurations', 'jira_tickets']:
    print(t, con.execute(f"SELECT count(*) FROM {t}").fetchone()[0])
