"""
RFC 6238 TOTP (Time-Based One-Time Password) Implementation for Coneza.
Compatible with Google Authenticator, Microsoft Authenticator, FreeOTP, and 1Password.
Pure Python standard library (hmac, hashlib, base64, struct, time, secrets).
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
import urllib.parse
from typing import Tuple, Optional

def generate_totp_secret(length: int = 20) -> str:
    """Generates a random Base32-encoded 160-bit secret."""
    random_bytes = secrets.token_bytes(length)
    secret = base64.b32encode(random_bytes).decode("utf-8").replace("=", "")
    return secret

def format_secret_for_display(secret: str) -> str:
    """Formats secret into 4-character chunks for human readability."""
    clean = secret.replace(" ", "").upper()
    return " ".join([clean[i:i+4] for i in range(0, len(clean), 4)])

def get_totp_code(secret: str, interval: int = 30, for_time: Optional[float] = None) -> str:
    """Calculates the current 6-digit TOTP code for the given secret."""
    clean_secret = secret.replace(" ", "").upper()
    # Add Base32 padding if needed
    padding = (8 - len(clean_secret) % 8) % 8
    key = base64.b32decode(clean_secret + "=" * padding)

    timestamp = for_time if for_time is not None else time.time()
    counter = int(timestamp // interval)

    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[19] & 0x0F
    code_int = (struct.unpack(">I", digest[offset:offset+4])[0] & 0x7FFFFFFF) % 1000000
    return f"{code_int:06d}"

def verify_totp_code(secret: str, code: str, window: int = 1, interval: int = 30) -> bool:
    """
    Verifies a 6-digit code against the secret within a drift window (default +/- 1 window = +/- 30s).
    """
    if not secret or not code:
        return False
    code_str = str(code).strip()
    if len(code_str) != 6 or not code_str.isdigit():
        return False

    clean_secret = secret.replace(" ", "").upper()
    try:
        padding = (8 - len(clean_secret) % 8) % 8
        key = base64.b32decode(clean_secret + "=" * padding)
    except Exception:
        return False

    current_counter = int(time.time() // interval)
    for offset in range(-window, window + 1):
        counter = current_counter + offset
        msg = struct.pack(">Q", counter)
        digest = hmac.new(key, msg, hashlib.sha1).digest()
        idx = digest[19] & 0x0F
        expected_code = (struct.unpack(">I", digest[idx:idx+4])[0] & 0x7FFFFFFF) % 1000000
        if f"{expected_code:06d}" == code_str:
            return True
    return False

def generate_otpauth_url(username: str, secret: str, issuer: str = "Coneza Portal") -> str:
    """Generates standard otpauth:// URL for scanning into Authenticator apps."""
    clean_secret = secret.replace(" ", "").upper()
    label = urllib.parse.quote(f"{issuer}:{username}")
    issuer_param = urllib.parse.quote(issuer)
    return f"otpauth://totp/{label}?secret={clean_secret}&issuer={issuer_param}&algorithm=SHA1&digits=6&period=30"
