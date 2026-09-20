"""
Database layer for coneza Central Backend using SQLite.
Stores Users, Linux Edge Devices, Documents (E8, E9, SLD), Gemini Analysis Jobs, and EZA Configurations.
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

def get_db_path() -> str:
    return os.getenv("CONEZA_DB_PATH", os.path.join(os.path.dirname(__file__), "coneza_backend.db"))

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite schema tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'VIEWER', -- 'SUPER_ADMIN', 'ENGINEER', 'VIEWER'
        totp_secret TEXT DEFAULT NULL,
        is_2fa_enabled INTEGER DEFAULT 0,
        must_change_password INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Automatic schema migration for existing databases
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if "totp_secret" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT DEFAULT NULL")
    if "is_2fa_enabled" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_2fa_enabled INTEGER DEFAULT 0")
    if "must_change_password" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plants (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        site_type TEXT NOT NULL DEFAULT 'PV', -- 'PV', 'BESS', 'WIND', 'HYBRID'
        grid_operator TEXT NOT NULL DEFAULT 'Bayernwerk Netz GmbH',
        voltage_level TEXT NOT NULL DEFAULT 'MS_4110', -- 'MS_4110', 'HS_4120', 'NS_4105'
        installed_capacity_kw REAL NOT NULL DEFAULT 0.0,
        grid_connection_point TEXT,
        location TEXT,
        commissioning_date TEXT,
        status TEXT NOT NULL DEFAULT 'PLANNING', -- 'PLANNING', 'COMMISSIONING', 'ONLINE_REGULATING', 'MAINTENANCE'
        notes TEXT DEFAULT '',
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        plant_id TEXT DEFAULT NULL,
        name TEXT NOT NULL,
        local_ip TEXT NOT NULL,
        os_platform TEXT,
        controller_host TEXT,
        controller_port INTEGER,
        status TEXT DEFAULT 'OFFLINE', -- 'ONLINE', 'OFFLINE', 'SYNCING'
        controller_state TEXT DEFAULT 'UNKNOWN',
        last_heartbeat TIMESTAMP,
        telemetry_json TEXT DEFAULT '{}',
        pending_config_json TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants (id)
    );
    """)

    # Migration for devices.plant_id
    cursor.execute("PRAGMA table_info(devices)")
    dev_cols = [r[1] for r in cursor.fetchall()]
    if "plant_id" not in dev_cols:
        cursor.execute("ALTER TABLE devices ADD COLUMN plant_id TEXT DEFAULT NULL")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        plant_id TEXT DEFAULT NULL,
        device_id TEXT,
        doc_type TEXT NOT NULL, -- 'E8', 'E9', 'SLD'
        filename TEXT NOT NULL,
        file_path TEXT,
        ocr_data_json TEXT NOT NULL DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants (id),
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    );
    """)

    # Migration for documents.plant_id
    cursor.execute("PRAGMA table_info(documents)")
    doc_cols = [r[1] for r in cursor.fetchall()]
    if "plant_id" not in doc_cols:
        cursor.execute("ALTER TABLE documents ADD COLUMN plant_id TEXT DEFAULT NULL")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_jobs (
        id TEXT PRIMARY KEY,
        device_id TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'ANALYZING', 'COMPLETED', 'FAILED'
        document_ids_json TEXT DEFAULT '[]',
        extracted_parameters_json TEXT DEFAULT '{}',
        discrepancies_json TEXT DEFAULT '[]',
        recommended_eza_config_json TEXT DEFAULT '{}',
        gemini_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eza_configurations (
        id TEXT PRIMARY KEY,
        device_id TEXT NOT NULL,
        analysis_job_id TEXT,
        parameters_json TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'DRAFT', -- 'DRAFT', 'APPROVED', 'DEPLOYED', 'FAILED'
        verification_log_json TEXT DEFAULT '[]',
        deployed_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        deployed_at TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (device_id),
        FOREIGN KEY (analysis_job_id) REFERENCES analysis_jobs (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_items (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL, -- 'DSO_PROFILE', 'LAYOUT_PATTERN', 'EZA_OPTIMIZATION', 'PLANT_BENCHMARK'
        pattern_key TEXT NOT NULL,
        data_json TEXT NOT NULL DEFAULT '{}',
        confidence_score REAL DEFAULT 0.85,
        observations_count INTEGER DEFAULT 1,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_events (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL, -- 'UNATTENDED_INGEST', 'KNOWLEDGE_LEARNED', 'CONFIG_AUTO_OPTIMIZED'
        doc_id TEXT,
        device_id TEXT,
        details_json TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jira_tickets (
        id TEXT PRIMARY KEY,
        jira_key TEXT,
        summary TEXT NOT NULL,
        description TEXT,
        issue_type TEXT DEFAULT 'Task',
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'OPEN',
        assignee TEXT,
        labels_json TEXT DEFAULT '[]',
        plant_id TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        synced_with_jira INTEGER DEFAULT 0
    );
    """)

    conn.commit()
    conn.close()
