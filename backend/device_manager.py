"""
Fleet Device Manager for coneza Central Backend.
Manages multiple local Linux devices, tracks their heartbeats and telemetry,
and orchestrates configuration deployments to Phoenix Contact EZA controllers.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database import get_connection

logger = logging.getLogger("coneza_device_manager")

class FleetDeviceManager:
    """Manages registered Linux edge devices and controller deployment pipelines."""

    def register_or_update_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()

        cursor.execute("SELECT device_id FROM devices WHERE device_id = ?", (data["device_id"],))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE devices SET
                    name = ?,
                    local_ip = ?,
                    device_category = ?,
                    manufacturer = ?,
                    model = ?,
                    slave_id = ?,
                    os_platform = ?,
                    controller_host = ?,
                    controller_port = ?,
                    status = 'ONLINE',
                    last_heartbeat = ?
                WHERE device_id = ?
            """, (
                data.get("name", "Edge Device"),
                data.get("local_ip", "127.0.0.1"),
                data.get("device_category", "EZA_CONTROLLER"),
                data.get("manufacturer", "Phoenix Contact"),
                data.get("model", "PLCnext SOL-SC-PCU"),
                data.get("slave_id", 1),
                data.get("os_platform", "Linux"),
                data.get("controller_host", "127.0.0.1"),
                data.get("controller_port", 5502),
                now,
                data["device_id"]
            ))
        else:
            cursor.execute("""
                INSERT INTO devices (
                    device_id, name, local_ip, device_category,
                    manufacturer, model, slave_id, os_platform,
                    controller_host, controller_port, status,
                    last_heartbeat, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ONLINE', ?, ?)
            """, (
                data["device_id"],
                data.get("name", "Edge Device"),
                data.get("local_ip", "127.0.0.1"),
                data.get("device_category", "EZA_CONTROLLER"),
                data.get("manufacturer", "Phoenix Contact"),
                data.get("model", "PLCnext SOL-SC-PCU"),
                data.get("slave_id", 1),
                data.get("os_platform", "Linux"),
                data.get("controller_host", "127.0.0.1"),
                data.get("controller_port", 5502),
                now,
                now
            ))

        conn.commit()
        conn.close()
        return self.get_device(data["device_id"])

    def process_heartbeat(self, device_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()

        cursor.execute("SELECT pending_config_json FROM devices WHERE device_id = ?", (device_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        pending_config = json.loads(row["pending_config_json"]) if row["pending_config_json"] else None
        if pending_config:
            from backend.configuration_safety import require_reviewable_configuration
            try:
                reviewed = require_reviewable_configuration(conn, pending_config["job_id"])
                state = conn.execute("SELECT status FROM eza_configurations WHERE id = ?",
                                     (pending_config["job_id"],)).fetchone()
                if state["status"] != "DEPLOYING" or pending_config.get("parameters") != reviewed:
                    raise ValueError("Queued configuration is no longer eligible")
            except (ValueError, KeyError, TypeError):
                pending_config = None
                cursor.execute("UPDATE devices SET pending_config_json = NULL WHERE device_id = ?", (device_id,))


        cursor.execute("""
            UPDATE devices SET
                status = 'ONLINE',
                local_ip = ?,
                controller_state = ?,
                telemetry_json = ?,
                last_heartbeat = ?
            WHERE device_id = ?
        """, (
            payload.get("local_ip", "127.0.0.1"),
            payload.get("controller_state", "Disconnected"),
            json.dumps(payload.get("telemetry", {})),
            now,
            device_id
        ))

        conn.commit()
        conn.close()

        return pending_config

    def queue_configuration_deployment(self, device_id: str, config_id: str, parameters: Dict[str, Any]):
        """Queues an approved configuration to be pushed to the Phoenix EZA controller."""
        conn = get_connection()
        cursor = conn.cursor()

        from backend.configuration_safety import require_reviewable_configuration
        try:
            conn.execute("BEGIN IMMEDIATE")
            reviewed = require_reviewable_configuration(conn, config_id, require_approved=True)
            if parameters != reviewed:
                raise ValueError("Deployment parameters differ from approved configuration")
        except Exception:
            conn.close()
            raise

        job_payload = {
            "job_id": config_id,
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat()
        }

        cursor.execute("""
            UPDATE devices SET pending_config_json = ? WHERE device_id = ?
        """, (json.dumps(job_payload), device_id))

        cursor.execute("""
            UPDATE eza_configurations SET status = 'DEPLOYING' WHERE id = ?
        """, (config_id,))

        conn.commit()
        conn.close()

    def record_deployment_result(self, job_id: str, device_id: str, success: bool, log: List[Dict[str, Any]]):
        """Records the Modbus verification log returned by the edge device."""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        status = "DEPLOYED" if success else "FAILED"

        cursor.execute("""
            UPDATE eza_configurations SET
                status = ?,
                verification_log_json = ?,
                deployed_at = ?
            WHERE id = ?
        """, (status, json.dumps(log), now, job_id))

        # Clear pending configuration from device record
        cursor.execute("""
            UPDATE devices SET pending_config_json = NULL WHERE device_id = ?
        """, (device_id,))

        conn.commit()
        conn.close()

    def list_devices(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        result = []
        for r in rows:
            d = dict(r)
            d["telemetry"] = json.loads(d["telemetry_json"]) if d["telemetry_json"] else {}
            d["has_pending_config"] = bool(d["pending_config_json"])
            del d["telemetry_json"]
            del d["pending_config_json"]
            result.append(d)
        return result

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        d["telemetry"] = json.loads(d["telemetry_json"]) if d["telemetry_json"] else {}
        d["has_pending_config"] = bool(d["pending_config_json"])
        del d["telemetry_json"]
        del d["pending_config_json"]
        return d

fleet_manager = FleetDeviceManager()
