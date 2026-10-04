import imaplib
import ssl

try:
    print("Connecting to mail.coneza.de:993...")
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    mail = imaplib.IMAP4_SSL("195.90.215.204", 993, ssl_context=context)
    print("Connected! Attempting IMAP login for s.saleem@coneza.de...")
    res = mail.login("s.saleem@coneza.de", "ConezaSecure2026!")
    print("IMAP Login Result:", res)
    mail.logout()
    print("SUCCESS: IMAP login succeeded with ConezaSecure2026!")
except Exception as e:
    print("IMAP Login Error:", e)
