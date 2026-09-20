import sqlite3
import os
import bcrypt

def hash_pw(pw):
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

db_path = os.getenv("CONEZA_DB_PATH", "/data/coneza_backend.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Set admin password to conezaAdmin2026! with must_change_password = 1
c.execute("""
    UPDATE users 
    SET hashed_password = ?, must_change_password = 1, is_2fa_enabled = 0, totp_secret = NULL
    WHERE username = 'admin'
""", (hash_pw("conezaAdmin2026!"),))

# Set engineer and viewer to must_change_password = 1 as well
c.execute("""
    UPDATE users 
    SET hashed_password = ?, must_change_password = 1, is_2fa_enabled = 0, totp_secret = NULL
    WHERE username = 'engineer'
""", (hash_pw("engineer2026!"),))

c.execute("""
    UPDATE users 
    SET hashed_password = ?, must_change_password = 1, is_2fa_enabled = 0, totp_secret = NULL
    WHERE username = 'viewer'
""", (hash_pw("viewer2026!"),))

conn.commit()
print("Reset default users with must_change_password = 1 successfully.")
