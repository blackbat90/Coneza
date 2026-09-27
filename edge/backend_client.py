"""
coneza Edge Backend Client & Sync Worker
Handles registration with central backend, periodic telemetry heartbeats,
document synchronization, and executing controller deployment jobs.
"""

import asyncio
import socket
import logging
import platform
import httpx
from typing import Dict, Any, Optional
from edge.phoenix_eza.controller import PhoenixEZAControllerClient

logger = logging.getLogger("coneza_edge_client")

class EdgeBackendClient:
    def __init__(
        self,
        backend_url: str = "http://127.0.0.1:8080",
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        controller_host: str = "127.0.0.1",
        controller_port: int = 5502,
        heartbeat_interval_sec: float = 10.0
    ):
        self.backend_url = backend_url.rstrip("/")
        self.hostname = socket.gethostname()
        self.device_id = device_id or f"coneza-edge-{self.hostname.lower()}"
        self.device_name = device_name or f"Edge Gateway ({self.hostname})"
        self.controller_host = controller_host
        self.controller_port = controller_port
        self.heartbeat_interval_sec = heartbeat_interval_sec
        self.controller_client = PhoenixEZAControllerClient(host=controller_host, port=controller_port)
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_sync_status: Dict[str, Any] = {"status": "INITIALIZING", "error": None}

    def _http_client(self, **kwargs):
        return httpx.AsyncClient(**kwargs)

    def get_local_ip(self) -> str:
        """Determines active local LAN IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    async def register_device(self) -> bool:
        """Registers this edge Linux device with the central backend."""
        payload = {
            "device_id": self.device_id,
            "name": self.device_name,
            "local_ip": self.get_local_ip(),
            "os_platform": platform.platform(),
            "controller_host": self.controller_host,
            "controller_port": self.controller_port,
        }
        try:
            async with self._http_client(timeout=5.0) as client:
                resp = await client.post(f"{self.backend_url}/api/devices/register", json=payload)
                if resp.status_code in (200, 201):
                    logger.info(f"Registered with backend: {self.device_id}")
                    self.last_sync_status = {"status": "REGISTERED", "error": None}
                    return True
                else:
                    logger.warning(f"Registration returned code {resp.status_code}: {resp.text}")
                    self.last_sync_status = {"status": "REGISTRATION_FAILED", "error": resp.text}
                    return False
        except Exception as e:
            logger.debug(f"Could not connect to backend at {self.backend_url}: {e}")
            self.last_sync_status = {"status": "BACKEND_OFFLINE", "error": str(e)}
            return False

    async def send_heartbeat(self):
        """Sends periodic heartbeat with live Phoenix Contact EZA telemetry."""
        controller_conn = await self.controller_client.test_connection()
        telemetry = {}
        if controller_conn.get("connected"):
            try:
                telemetry = await self.controller_client.read_telemetry()
            except Exception as e:
                logger.warning(f"Failed to read telemetry during heartbeat: {e}")
                controller_conn = {"connected": False, "controller_state": "TELEMETRY_UNAVAILABLE"}

        payload = {
            "device_id": self.device_id,
            "local_ip": self.get_local_ip(),
            "controller_connected": controller_conn.get("connected", False),
            "controller_state": controller_conn.get("controller_state", "Disconnected"),
            "telemetry": telemetry
        }

        try:
            async with self._http_client(timeout=5.0) as client:
                resp = await client.post(f"{self.backend_url}/api/devices/{self.device_id}/heartbeat", json=payload)
                if resp.status_code == 200:
                    self.last_sync_status = {"status": "ONLINE", "error": None}
                    data = resp.json()
                    # Check if any configuration deployment job is pending
                    pending_config = data.get("pending_configuration")
                    if pending_config:
                        await self._execute_pending_config(pending_config)
                elif resp.status_code == 404:
                    # Device not registered in backend DB yet, re-register
                    await self.register_device()
                else:
                    # A rejected heartbeat must not leave an earlier ONLINE visible.
                    self.last_sync_status = {
                        "status": "HEARTBEAT_FAILED", "error": f"HTTP {resp.status_code}"
                    }
        except Exception as e:
            self.last_sync_status = {"status": "HEARTBEAT_FAILED", "error": str(e)}

    async def _execute_pending_config(self, job: Dict[str, Any]):
        """Executes a pending EZA configuration job dispatched by the backend."""
        if not isinstance(job, dict):
            raise ValueError("Configuration job must be an object")
        job_id = job.get("job_id")
        config_params = job.get("parameters")
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("Configuration job requires a non-empty string job_id")
        if not isinstance(config_params, dict):
            raise ValueError("Configuration job requires a parameters object")
        logger.info(f"Executing pending EZA configuration job {job_id} on Phoenix controller...")

        result = await self.controller_client.apply_configuration(config_params, verify=True)
        
        # Report execution result back to backend
        report_payload = {
            "job_id": job_id,
            "device_id": self.device_id,
            "success": result["success"],
            "verification_log": result["verification_log"],
            "registers_updated": result["registers_updated"]
        }
        try:
            async with self._http_client(timeout=5.0) as client:
                response = await client.post(f"{self.backend_url}/api/devices/{self.device_id}/config-result", json=report_payload)
                response.raise_for_status()
                logger.info(f"Reported config job {job_id} result: success={result['success']}")
        except Exception as e:
            logger.error(f"Failed to report config job {job_id} result to backend: {e}")

    async def forward_document_to_backend(self, doc_data: Dict[str, Any], file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Forwards an uploaded E8/E9/SLD document to the backend for Gemini analysis."""
        try:
            files = {"file": (filename, file_bytes, "application/pdf")}
            data = {
                "device_id": self.device_id,
                "doc_type": doc_data.get("detected_type", "E8"),
                "ocr_summary": str(doc_data.get("extracted_entities", {}))
            }
            async with self._http_client(timeout=30.0) as client:
                resp = await client.post(f"{self.backend_url}/api/documents/upload", files=files, data=data)
                if resp.status_code in (200, 201):
                    return resp.json()
                else:
                    logger.error(f"Backend document upload error {resp.status_code}: {resp.text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to forward document to backend: {e}")
            return None

    async def _run_loop(self):
        """Main agent loop."""
        await self.register_device()
        while self.is_running:
            try:
                await self.send_heartbeat()
            except Exception as e:
                self.last_sync_status = {"status": "HEARTBEAT_FAILED", "error": "Heartbeat processing failed"}
                logger.error(f"Heartbeat loop error: {e}")
            await asyncio.sleep(self.heartbeat_interval_sec)

    def start(self):
        """Starts the backend sync loop."""
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("EdgeBackendClient started")

    async def stop(self):
        """Stops the backend sync loop."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("EdgeBackendClient stopped")
