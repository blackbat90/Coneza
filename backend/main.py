"""
coneza Central Backend Server
Orchestrates multiple Linux edge devices, receives E8, E9, and SLD files,
runs Gemini API grid compliance analysis, and manages Phoenix Contact EZA controller deployments.
Includes Role-Based Access Control (RBAC) with Super User device provisioning.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import HTTPAuthorizationCredentials
from backend.database import init_db, get_connection
from backend.models import (
    UserCreate, UserLogin, UserResponse, UserRoleUpdate,
    TwoFactorVerifyLogin, TwoFactorEnableRequest, TwoFactorDisableRequest, PasswordChangeRequest,
    DeviceRegister, DeviceHeartbeat, DeviceResponse,
    AnalysisTrigger, ConfigDeployRequest
)
from backend.auth import (
    hash_password, verify_password, create_access_token, create_temp_token,
    decode_access_token, decode_scoped_token, security,
    get_current_user, require_super_user, require_engineer, require_viewer
)
from backend.totp_auth import (
    generate_totp_secret, format_secret_for_display,
    get_totp_code, verify_totp_code, generate_otpauth_url
)
from backend.device_manager import fleet_manager
from backend.gemini_analyzer import gemini_analyzer
from backend.continuous_improver import continuous_improver
from edge.ocr_engine import ocr_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("coneza_backend_server")

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "stored_documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed Default Super User
    init_db()
    seed_default_users()
    logger.info("coneza Central Backend initialized successfully.")
    yield

app = FastAPI(
    title="coneza Central Backend",
    description="Central Management Server for Linux Edge Devices, Gemini Analysis & Phoenix Contact EZA Controller Deployment",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/health")
async def health_check():
    """Unauthenticated health check for docker healthchecks and load balancers."""
    return {"status": "ok", "service": "coneza-backend"}

def seed_default_users():
    """Seeds default Super User, Engineer, and Viewer accounts if DB is fresh, enforcing initial password reset."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        logger.info("Seeding initial users with mandatory password change (admin, engineer, viewer)...")
        # Super User
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, must_change_password)
            VALUES (?, ?, ?, ?, 1)
        """, ("admin", "admin@coneza.local", hash_password("conezaAdmin2026!"), "SUPER_ADMIN"))

        # Commissioning Engineer
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, must_change_password)
            VALUES (?, ?, ?, ?, 1)
        """, ("engineer", "engineer@coneza.local", hash_password("engineer2026!"), "ENGINEER"))

        # Read-only Viewer
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, must_change_password)
            VALUES (?, ?, ?, ?, 1)
        """, ("viewer", "viewer@coneza.local", hash_password("viewer2026!"), "VIEWER"))

        # Seed sample demo device
        cursor.execute("""
            INSERT INTO devices (device_id, name, local_ip, os_platform, controller_host, controller_port, status, controller_state, last_heartbeat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "coneza-edge-solar-park-01",
            "Solar Park West - Inverter Station 1",
            "192.168.10.15",
            "Linux (Ubuntu 24.04 LTS / Phoenix EPC 1502)",
            "192.168.10.20",
            5502,
            "ONLINE",
            "ONLINE_REGULATING",
            datetime.utcnow().isoformat()
        ))
        conn.commit()
    else:
        # Enforce password reset on existing default accounts
        cursor.execute("""
            UPDATE users SET must_change_password = 1
            WHERE username IN ('admin', 'engineer', 'viewer') AND (must_change_password IS NULL OR must_change_password = 0)
        """)
        conn.commit()
    conn.close()

# ----------------- Authentication Endpoints ----------------- #

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (credentials.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = user["id"]
    username = user["username"]
    role = user["role"]
    is_2fa = bool(user["is_2fa_enabled"] if "is_2fa_enabled" in user.keys() else False)
    must_change = bool(user["must_change_password"] if "must_change_password" in user.keys() else False)

    # 1. Two-Factor Authentication Check
    if is_2fa:
        totp_secret = user["totp_secret"] if "totp_secret" in user.keys() else None
        valid_totp = False
        if credentials.totp_code and totp_secret:
            valid_totp = verify_totp_code(totp_secret, credentials.totp_code)

        if not valid_totp:
            temp_token = create_temp_token(user_id, username, role, scope="2fa_challenge")
            return {
                "status": "2FA_REQUIRED",
                "is_2fa_required": True,
                "temp_token": temp_token,
                "message": "Zwei-Faktor-Authentifizierung erforderlich. Bitte geben Sie Ihren 6-stelligen Code aus Ihrer Authenticator-App ein."
            }

    # 2. Mandatory Password Reset Check
    if must_change:
        temp_token = create_temp_token(user_id, username, role, scope="password_reset")
        return {
            "status": "PASSWORD_RESET_REQUIRED",
            "must_change_password": True,
            "temp_token": temp_token,
            "user": {
                "id": user_id,
                "username": username,
                "email": user["email"],
                "role": role
            },
            "message": "Passwortänderung erforderlich: Aus Sicherheitsgründen müssen Sie Ihr Initialpasswort ändern."
        }

    # 3. Successful Direct Login
    token = create_access_token(user_id, username, role)
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": username,
            "email": user["email"],
            "role": role,
            "is_2fa_enabled": 1 if is_2fa else 0,
            "must_change_password": 0
        }
    }

@app.post("/api/auth/2fa/verify-login")
async def verify_login_2fa(payload: TwoFactorVerifyLogin):
    token_data = decode_scoped_token(payload.temp_token, expected_scope="2fa_challenge")
    if not token_data:
        raise HTTPException(status_code=401, detail="Sitzung abgelaufen oder ungültig. Bitte erneut anmelden.")

    user_id = int(token_data["sub"])
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    totp_secret = user["totp_secret"]
    if not totp_secret or not verify_totp_code(totp_secret, payload.totp_code):
        raise HTTPException(status_code=400, detail="Ungültiger 2FA-Code. Bitte prüfen Sie die Uhrzeit und Ihre App.")

    # Check if forced password reset is required after 2FA succeeds
    if bool(user["must_change_password"]):
        temp_token = create_temp_token(user["id"], user["username"], user["role"], scope="password_reset")
        return {
            "status": "PASSWORD_RESET_REQUIRED",
            "must_change_password": True,
            "temp_token": temp_token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            },
            "message": "Passwortänderung erforderlich: Aus Sicherheitsgründen müssen Sie Ihr Initialpasswort ändern."
        }

    token = create_access_token(user["id"], user["username"], user["role"])
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "is_2fa_enabled": 1,
            "must_change_password": 0
        }
    }

@app.post("/api/auth/change-password")
async def change_password(payload: PasswordChangeRequest, creds: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Handles forced password change or voluntary password updates."""
    user_id = None
    if payload.temp_token:
        token_data = decode_scoped_token(payload.temp_token, expected_scope="password_reset")
        if token_data:
            user_id = int(token_data["sub"])

    if not user_id and creds:
        token_data = decode_access_token(creds.credentials)
        if token_data and token_data.get("sub"):
            user_id = int(token_data["sub"])

    if not user_id:
        raise HTTPException(status_code=401, detail="Nicht autorisiert: Ungültiges oder abgelaufenes Token.")

    new_pw = payload.new_password.strip()
    if len(new_pw) < 8:
        raise HTTPException(status_code=400, detail="Das neue Passwort muss mindestens 8 Zeichen lang sein.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    # If old password was supplied, verify it
    if payload.old_password:
        if not verify_password(payload.old_password, user["hashed_password"]):
            conn.close()
            raise HTTPException(status_code=400, detail="Das bisherige Passwort ist nicht korrekt.")

    # New password cannot be identical to current password
    if verify_password(new_pw, user["hashed_password"]):
        conn.close()
        raise HTTPException(status_code=400, detail="Das neue Passwort darf nicht mit dem bisherigen Passwort identisch sein.")

    new_hashed = hash_password(new_pw)
    cursor.execute("UPDATE users SET hashed_password = ?, must_change_password = 0 WHERE id = ?", (new_hashed, user_id))
    conn.commit()
    conn.close()

    new_token = create_access_token(user_id, user["username"], user["role"])
    return {
        "status": "success",
        "message": "Passwort erfolgreich aktualisiert!",
        "access_token": new_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "is_2fa_enabled": user["is_2fa_enabled"] or 0,
            "must_change_password": 0
        }
    }

@app.get("/api/auth/2fa/setup")
async def setup_2fa(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns TOTP secret, formatted key, and otpauth URL for Google/Microsoft Authenticator."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT totp_secret, is_2fa_enabled FROM users WHERE id = ?", (current_user["id"],))
    row = cursor.fetchone()

    secret = row["totp_secret"] if (row and row["totp_secret"]) else generate_totp_secret()
    if not row or not row["totp_secret"]:
        cursor.execute("UPDATE users SET totp_secret = ? WHERE id = ?", (secret, current_user["id"]))
        conn.commit()
    conn.close()

    otpauth_url = generate_otpauth_url(current_user["username"], secret)
    return {
        "secret": secret,
        "formatted_secret": format_secret_for_display(secret),
        "otpauth_url": otpauth_url,
        "is_2fa_enabled": bool(row["is_2fa_enabled"] if row else False)
    }

@app.post("/api/auth/2fa/enable")
async def enable_2fa(payload: TwoFactorEnableRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verifies a 6-digit TOTP code and activates 2FA for the authenticated user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT totp_secret FROM users WHERE id = ?", (current_user["id"],))
    row = cursor.fetchone()

    if not row or not row["totp_secret"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Kein 2FA-Schlüssel initialisiert. Bitte rufen Sie zuerst /setup auf.")

    if not verify_totp_code(row["totp_secret"], payload.totp_code):
        conn.close()
        raise HTTPException(status_code=400, detail="Ungültiger 2FA-Code. Bitte prüfen Sie Ihre Authenticator-App.")

    cursor.execute("UPDATE users SET is_2fa_enabled = 1 WHERE id = ?", (current_user["id"],))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Zwei-Faktor-Authentifizierung (2FA) wurde erfolgreich aktiviert!"}

@app.post("/api/auth/2fa/disable")
async def disable_2fa(payload: TwoFactorDisableRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Disables 2FA (requires password confirmation)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (current_user["id"],))
    row = cursor.fetchone()

    if not row or not verify_password(payload.password, row["hashed_password"]):
        conn.close()
        raise HTTPException(status_code=400, detail="Ungültiges Passwort.")

    cursor.execute("UPDATE users SET is_2fa_enabled = 0, totp_secret = NULL WHERE id = ?", (current_user["id"],))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "2FA wurde deaktiviert."}

@app.post("/api/auth/users/{user_id}/force-reset-password", dependencies=[Depends(require_super_user)])
async def admin_force_reset_password(user_id: int):
    """Super Admin forces a user to reset their password upon their next login."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET must_change_password = 1 WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Passwort-Reset für Benutzer {user_id} wurde erzwungen."}

@app.post("/api/auth/users/{user_id}/reset-2fa", dependencies=[Depends(require_super_user)])
async def admin_reset_2fa(user_id: int):
    """Super Admin resets 2FA for a user (e.g. if their authenticator phone was lost)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_2fa_enabled = 0, totp_secret = NULL WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"2FA für Benutzer {user_id} wurde erfolgreich zurückgesetzt."}


@app.post("/api/auth/register")
async def register(payload: UserCreate):
    """Public registration endpoint for new users."""
    username = payload.username.strip()
    email = payload.email.strip()
    password = payload.password

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email, and password are required")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Self-registration cannot create SUPER_ADMIN directly; must be ENGINEER or VIEWER
    role = payload.role if payload.role in ("ENGINEER", "VIEWER") else "VIEWER"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already taken")

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, hash_password(password), role))
        user_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Registration failed: {e}")
    conn.close()

    token = create_access_token(user_id, username, role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": username,
            "email": email,
            "role": role
        }
    }

@app.get("/api/auth/me")
async def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return user

@app.post("/api/auth/users", dependencies=[Depends(require_super_user)])
async def create_user(payload: UserCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role)
            VALUES (?, ?, ?, ?)
        """, (payload.username, payload.email, hash_password(payload.password), payload.role))
        user_id = cursor.lastrowid
        conn.commit()
        return {"id": user_id, "username": payload.username, "email": payload.email, "role": payload.role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User creation failed: {e}")
    finally:
        conn.close()

@app.get("/api/auth/users", dependencies=[Depends(require_super_user)])
async def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, is_2fa_enabled, must_change_password, created_at FROM users ORDER BY id ASC")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return users


@app.delete("/api/auth/users/{user_id}", dependencies=[Depends(require_super_user)])
async def delete_user(user_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    if int(current_user["id"]) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own active admin account")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"User {user_id} deleted"}

@app.patch("/api/auth/users/{user_id}/role", dependencies=[Depends(require_super_user)])
async def update_user_role(user_id: int, payload: UserRoleUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    if payload.role not in ("SUPER_ADMIN", "ENGINEER", "VIEWER"):
        raise HTTPException(status_code=400, detail="Invalid role. Must be SUPER_ADMIN, ENGINEER, or VIEWER")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (payload.role, user_id))
    conn.commit()
    conn.close()
    return {"status": "success", "user_id": user_id, "new_role": payload.role}

# ----------------- Multi-Device Fleet Endpoints ----------------- #

@app.get("/api/devices")
async def list_devices(user: Dict[str, Any] = Depends(require_viewer)):
    """Lists all registered Linux edge devices across the local networks."""
    return fleet_manager.list_devices()

@app.post("/api/devices/register")
async def register_device(payload: DeviceRegister):
    """Edge Linux devices register themselves with the backend."""
    device = fleet_manager.register_or_update_device(payload.model_dump())
    return device

@app.get("/api/devices/{device_id}")
async def get_device(device_id: str, user: Dict[str, Any] = Depends(require_viewer)):
    device = fleet_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.post("/api/devices/{device_id}/heartbeat")
async def device_heartbeat(device_id: str, payload: DeviceHeartbeat):
    pending_config = fleet_manager.process_heartbeat(device_id, payload.model_dump())
    return {
        "status": "acknowledged",
        "pending_configuration": pending_config
    }

@app.post("/api/devices/{device_id}/config-result")
async def device_config_result(device_id: str, payload: Dict[str, Any]):
    fleet_manager.record_deployment_result(
        job_id=payload["job_id"],
        device_id=device_id,
        success=payload["success"],
        log=payload.get("verification_log", [])
    )
    return {"status": "recorded"}

@app.post("/api/devices/provision", dependencies=[Depends(require_super_user)])
async def superuser_provision_device(payload: DeviceRegister):
    """Super User manually provisions a remote Linux edge device."""
    device = fleet_manager.register_or_update_device(payload.model_dump())
    return {"status": "provisioned", "device": device}

# ----------------- Document Management (E8, E9, SLD) ----------------- #

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    device_id: Optional[str] = Form(None),
    doc_type: Optional[str] = Form(None),
    ocr_summary: Optional[str] = Form(None)
):
    """Receives and parses E8, E9, or SLD PDF files, triggering unattended continuous improvement."""
    try:
        content = await file.read()
        filename = file.filename or "grid_doc.pdf"
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        # Save locally
        save_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}_{filename}")
        with open(save_path, "wb") as f:
            f.write(content)

        # Run OCR extraction
        ocr_result = ocr_engine.extract_document(content, filename)
        if doc_type and doc_type in ("E8", "E9", "SLD"):
            ocr_result["detected_type"] = doc_type

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, device_id, doc_type, filename, file_path, ocr_data_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            device_id,
            ocr_result["detected_type"],
            filename,
            save_path,
            json.dumps(ocr_result)
        ))
        conn.commit()
        conn.close()

        # Autonomous unattended continuous improvement triggered immediately in background
        background_tasks.add_task(
            continuous_improver.process_uploaded_document_unattended,
            doc_id,
            device_id
        )

        return {
            "id": doc_id,
            "filename": filename,
            "detected_type": ocr_result["detected_type"],
            "total_pages": ocr_result["total_pages"],
            "extracted_entities": ocr_result["extracted_entities"],
            "pipeline_status": "UNATTENDED_PROCESSING_TRIGGERED"
        }
    except Exception as e:
        logger.error(f"Failed to process document upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents(user: Dict[str, Any] = Depends(require_viewer)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, device_id, doc_type, filename, created_at, ocr_data_json FROM documents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        ocr_data = json.loads(d["ocr_data_json"])
        d["extracted_entities"] = ocr_data.get("extracted_entities", {})
        d["total_pages"] = ocr_data.get("total_pages", 1)
        del d["ocr_data_json"]
        result.append(d)
    return result

# ----------------- Gemini Analysis & Synthesis ----------------- #

@app.post("/api/analysis/run")
async def trigger_gemini_analysis(
    payload: AnalysisTrigger,
    user: Dict[str, Any] = Depends(require_engineer)
):
    """
    Triggers Gemini API analysis on E8, E9, and SLD documents.
    Cross-validates parameters and synthesizes Phoenix Contact EZA Controller configuration.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Load documents
    cursor.execute(f"SELECT * FROM documents WHERE id IN ({','.join(['?']*len(payload.document_ids))})", payload.document_ids)
    doc_rows = cursor.fetchall()

    if not doc_rows:
        conn.close()
        raise HTTPException(status_code=400, detail="No matching documents found for analysis")

    documents_payload = []
    for row in doc_rows:
        ocr_data = json.loads(row["ocr_data_json"])
        documents_payload.append({
            "id": row["id"],
            "filename": row["filename"],
            "doc_type": row["doc_type"],
            "ocr_entities": ocr_data.get("extracted_entities", {}),
            "full_text": ocr_data.get("full_text", "")
        })

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO analysis_jobs (id, device_id, status, document_ids_json)
        VALUES (?, ?, 'ANALYZING', ?)
    """, (job_id, payload.device_id, json.dumps(payload.document_ids)))
    conn.commit()

    # Run Gemini Analysis
    analysis_result = gemini_analyzer.analyze_documents(documents_payload)

    # Save Analysis Job
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        UPDATE analysis_jobs SET
            status = 'COMPLETED',
            extracted_parameters_json = ?,
            discrepancies_json = ?,
            recommended_eza_config_json = ?,
            gemini_summary = ?,
            completed_at = ?
        WHERE id = ?
    """, (
        json.dumps(analysis_result.get("extracted_parameters", {})),
        json.dumps(analysis_result.get("discrepancies", [])),
        json.dumps(analysis_result.get("recommended_eza_config", {})),
        analysis_result.get("summary", "Analysis completed."),
        now,
        job_id
    ))

    # Create associated EZA Configuration draft
    config_id = f"cfg_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO eza_configurations (id, device_id, analysis_job_id, parameters_json, status)
        VALUES (?, ?, ?, ?, 'DRAFT')
    """, (
        config_id,
        payload.device_id,
        job_id,
        json.dumps(analysis_result.get("recommended_eza_config", {}))
    ))

    conn.commit()
    conn.close()

    return {
        "job_id": job_id,
        "config_id": config_id,
        "status": "COMPLETED",
        "analysis": analysis_result
    }

@app.get("/api/analysis/{job_id}")
async def get_analysis_job(job_id: str, user: Dict[str, Any] = Depends(require_viewer)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    d = dict(row)
    d["extracted_parameters"] = json.loads(d["extracted_parameters_json"])
    d["discrepancies"] = json.loads(d["discrepancies_json"])
    d["recommended_eza_config"] = json.loads(d["recommended_eza_config_json"])
    del d["extracted_parameters_json"]
    del d["discrepancies_json"]
    del d["recommended_eza_config_json"]
    return d

# ----------------- Configuration & Deployment ----------------- #

@app.get("/api/configs")
async def list_configurations(user: Dict[str, Any] = Depends(require_viewer)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eza_configurations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d["parameters"] = json.loads(d["parameters_json"])
        d["verification_log"] = json.loads(d["verification_log_json"]) if d["verification_log_json"] else []
        del d["parameters_json"]
        del d["verification_log_json"]
        result.append(d)
    return result

@app.post("/api/configs/{config_id}/approve")
async def approve_configuration(
    config_id: str,
    user: Dict[str, Any] = Depends(require_super_user)
):
    """Super User approves the EZA configuration for plant deployment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE eza_configurations SET status = 'APPROVED' WHERE id = ?", (config_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "config_id": config_id, "state": "APPROVED"}

@app.post("/api/configs/deploy")
async def deploy_configuration(
    payload: ConfigDeployRequest,
    user: Dict[str, Any] = Depends(require_super_user)
):
    """Super User commands deployment to the designated Linux edge device."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT parameters_json, status FROM eza_configurations WHERE id = ?", (payload.config_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Configuration not found")

    params = json.loads(row["parameters_json"])
    fleet_manager.queue_configuration_deployment(
        device_id=payload.target_device_id,
        config_id=payload.config_id,
        parameters=params
    )

    return {
        "status": "QUEUED_FOR_DEPLOYMENT",
        "target_device_id": payload.target_device_id,
        "config_id": payload.config_id,
        "authorized_by": user["username"]
    }

# ----------------- Unattended Continuous Improvement Engine ----------------- #

@app.get("/api/improver/status")
async def get_improver_status(user: Dict[str, Any] = Depends(require_viewer)):
    """Returns real-time telemetry from the unattended continuous improvement engine."""
    return continuous_improver.get_telemetry()

@app.post("/api/improver/trigger-relearning", dependencies=[Depends(require_engineer)])
async def trigger_relearning(background_tasks: BackgroundTasks):
    """Triggers an unattended batch relearning pass across all stored grid documents."""
    background_tasks.add_task(continuous_improver.reprocess_all_unattended)
    return {"status": "BATCH_RELEARNING_TRIGGERED", "message": "Autonomous evaluation scheduled in background"}

@app.get("/", response_class=HTMLResponse)
async def serve_backend_ui():
    """Serves the central management UI dashboard."""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    index_file = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>coneza Central Backend</h1><p>Visit /docs for API documentation.</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
