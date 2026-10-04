"""
Local Store-and-Forward Telemetry Buffer for Coneza Edge Gateways.
Directly implements Confluence Requirement from 'Edge Cases':
- 'End user has no internet on site / temporary no or poor internet connection'
- 'Store & Forward local telemetry ring-buffer on Industrial IPC'

Safely queues telemetry readings, alarms, and setpoint acknowledgments in an on-disk
SQLite database when 4G/WAN connection is unavailable, and automatically flushes to
Coneza Central when network connectivity is re-established.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("coneza_local_buffer")

DEFAULT_BUFFER_DB = os.path.join(os.path.dirname(__file__), "edge_local_buffer.db")
MAX_BUFFER_ROWS = 50000


class LocalStoreAndForwardBuffer:
    """Manages offline telemetry persistence and synchronization on the Edge IPC."""

    def __init__(self, db_path: str = DEFAULT_BUFFER_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS buffered_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    is_synced INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sync_status ON buffered_telemetry(is_synced, id)
            """)
            conn.commit()

    def buffer_record(self, device_id: str, telemetry: Dict[str, Any]) -> int:
        """Saves a telemetry snapshot into the local offline buffer."""
        now_iso = datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(telemetry)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO buffered_telemetry (device_id, timestamp, payload_json, is_synced)
                VALUES (?, ?, ?, 0)
            """, (device_id, now_iso, payload_str))
            record_id = cursor.lastrowid

            # Ring buffer retention check: purge oldest synced records if size exceeds limit
            cursor.execute("SELECT COUNT(*) FROM buffered_telemetry")
            count = cursor.fetchone()[0]
            if count > MAX_BUFFER_ROWS:
                cursor.execute("""
                    DELETE FROM buffered_telemetry WHERE id IN (
                        SELECT id FROM buffered_telemetry WHERE is_synced = 1 ORDER BY id ASC LIMIT 5000
                    )
                """)
            conn.commit()
            return record_id

    def get_pending_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves un-synced telemetry packets waiting to be sent to Coneza Central."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, device_id, timestamp, payload_json, retry_count
                FROM buffered_telemetry
                WHERE is_synced = 0
                ORDER BY id ASC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "device_id": r["device_id"],
                    "timestamp": r["timestamp"],
                    "telemetry": json.loads(r["payload_json"]),
                    "retry_count": r["retry_count"]
                }
                for r in rows
            ]

    def mark_records_synced(self, record_ids: List[int]) -> None:
        """Marks successfully transmitted records as synced."""
        if not record_ids:
            return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            placeholders = ",".join("?" for _ in record_ids)
            cursor.execute(f"""
                UPDATE buffered_telemetry
                SET is_synced = 1
                WHERE id IN ({placeholders})
            """, record_ids)
            conn.commit()

    def get_buffer_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM buffered_telemetry WHERE is_synced = 0")
            pending = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM buffered_telemetry WHERE is_synced = 1")
            synced = cursor.fetchone()[0]
            return {
                "pending_offline_records": pending,
                "synced_records": synced,
                "total_records": pending + synced,
                "database_path": self.db_path
            }


# Global singleton instance
local_buffer = LocalStoreAndForwardBuffer()
