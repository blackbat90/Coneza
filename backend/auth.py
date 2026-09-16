"""
Authentication & Role-Based Access Control (RBAC) for coneza Central Backend.
Roles:
- SUPER_ADMIN: Universal access across all local Linux devices, can provision devices,
               approve & deploy Phoenix Contact EZA configurations, and manage users.
- ENGINEER: Can upload documents, run Gemini analyses, draft configurations, and test connections.
- VIEWER: Read-only access to devices, documents, and controller telemetry.
"""

import os
import time
import bcrypt
import jwt
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.database import get_connection

SECRET_KEY = os.getenv("CONEZA_JWT_SECRET", "coneza-super-secret-jwt-key-2026-vde4110")
ALGORITHM = "HS256"
TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
        "iat": int(time.time())
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Authenticates the bearer token and retrieves user record."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (payload["sub"],))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return dict(row)

def require_super_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Ensures caller has SUPER_ADMIN privileges."""
    if current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Super User privilege required to manage edge Linux devices and deploy configurations"
        )
    return current_user

def require_engineer(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Ensures caller has at least ENGINEER privileges."""
    if current_user["role"] not in ("SUPER_ADMIN", "ENGINEER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Engineer privilege required"
        )
    return current_user

def require_viewer(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Ensures caller is authenticated."""
    return current_user
