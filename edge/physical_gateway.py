"""
coneza Physical Phoenix Contact EZA Controller Gateway Runner
Connects to physical Phoenix Contact PLCnext (AXC F 2152) over Modbus TCP
and synchronizes live telemetry, status, and setpoints with the Coneza Portal.
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Optional

import httpx

from edge.backend_client import EdgeBackendClient
from edge.phoenix_eza.controller import PhoenixEZAControllerClient

logger = logging.getLogger("coneza_physical_gateway")


class PhysicalPhoenixGateway(EdgeBackendClient):
    """
    Edge Gateway specifically configured for physical Phoenix Contact PLCnext controllers.
    Supports either direct HTTPS or Unix domain socket relay to the Coneza Portal.
    """

    def __init__(
        self,
        backend_url: str = "https://coneza.de/portal",
        device_id: str = "coneza-phoenix-axcf2152",
        device_name: str = "Phoenix Contact AXC F 2152 (EZA-Regler)",
        controller_host: str = "192.168.1.10",
        controller_port: int = 502,
        portal_socket: Optional[str] = None,
        heartbeat_interval_sec: float = 10.0,
    ):
        super().__init__(
            backend_url=backend_url,
            device_id=device_id,
            device_name=device_name,
            controller_host=controller_host,
            controller_port=controller_port,
            heartbeat_interval_sec=heartbeat_interval_sec,
        )
        self.portal_socket = portal_socket

    def _http_client(self, **kwargs):
        if self.portal_socket and os.path.exists(self.portal_socket):
            kwargs["transport"] = httpx.AsyncHTTPTransport(uds=self.portal_socket, verify=True)
            kwargs["trust_env"] = False
        return httpx.AsyncClient(**kwargs)

    async def register_device(self) -> bool:
        """Registers the physical Phoenix PLC gateway with the central backend."""
        payload = {
            "device_id": self.device_id,
            "plant_id": os.getenv("PLANT_ID", "plant-solar-west-01"),
            "name": self.device_name,
            "local_ip": self.get_local_ip(),
            "os_platform": "PLCnext Linux 2026.6.0 (scarthgap) / Debian Linux IPC",
            "controller_host": self.controller_host,
            "controller_port": self.controller_port,
            "device_category": "EZA_CONTROLLER",
            "manufacturer": "Phoenix Contact",
            "model": "AXC F 2152",
            "slave_id": 1,
        }
        try:
            async with self._http_client(timeout=10.0) as client:
                resp = await client.post(f"{self.backend_url}/api/devices/register", json=payload)
                if resp.status_code in (200, 201):
                    logger.info("Successfully registered physical Phoenix PLC with portal: %s", self.device_id)
                    self.last_sync_status = {"status": "REGISTERED", "error": None}
                    return True
                else:
                    logger.warning("Registration returned %s: %s", resp.status_code, resp.text)
                    self.last_sync_status = {"status": "REGISTRATION_FAILED", "error": resp.text}
                    return False
        except Exception as e:
            logger.error("Could not register with portal at %s: %s", self.backend_url, e)
            self.last_sync_status = {"status": "BACKEND_OFFLINE", "error": str(e)}
            return False


async def run(stop_event: Optional[asyncio.Event] = None):
    backend_url = os.getenv("CONEZA_BACKEND_URL", "https://coneza.de/portal")
    device_id = os.getenv("DEVICE_ID", "coneza-phoenix-axcf2152")
    device_name = os.getenv("DEVICE_NAME", "Phoenix Contact AXC F 2152 (EZA-Regler)")
    controller_host = os.getenv("EZA_CONTROLLER_HOST", "192.168.1.10")
    controller_port = int(os.getenv("EZA_CONTROLLER_PORT", "502"))
    portal_socket = os.getenv("PORTAL_SOCKET")
    if not portal_socket and os.path.exists("/run/coneza-portal/portal.sock"):
        portal_socket = "/run/coneza-portal/portal.sock"

    logger.info("Initializing Phoenix EZA Gateway:")
    logger.info("  Device ID       : %s", device_id)
    logger.info("  Device Name     : %s", device_name)
    logger.info("  Controller Host : %s:%s", controller_host, controller_port)
    logger.info("  Portal URL      : %s", backend_url)
    logger.info("  Portal Socket   : %s", portal_socket or "None (direct HTTPS)")

    gateway = PhysicalPhoenixGateway(
        backend_url=backend_url,
        device_id=device_id,
        device_name=device_name,
        controller_host=controller_host,
        controller_port=controller_port,
        portal_socket=portal_socket,
        heartbeat_interval_sec=10.0,
    )

    # Initial controller connectivity check
    conn = await gateway.controller_client.test_connection()
    if conn.get("connected"):
        logger.info("PLC Connectivity: Connected to Phoenix Contact PLC (%s:%s)", controller_host, controller_port)
    else:
        logger.warning("PLC Connectivity Warning: Could not connect to %s:%s: %s",
                       controller_host, controller_port, conn.get("error"))

    stop = stop_event or asyncio.Event()
    loop = asyncio.get_running_loop()
    installed = []
    if stop_event is None:
        for signum in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(signum, stop.set)
            installed.append(signum)

    try:
        gateway.start()
        logger.info("Gateway service running. Press Ctrl+C or send SIGTERM to stop.")
        await stop.wait()
    finally:
        logger.info("Shutting down physical Phoenix gateway...")
        await gateway.stop()
        await gateway.controller_client.close()
        for signum in installed:
            loop.remove_signal_handler(signum)
        logger.info("Gateway stopped cleanly.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    asyncio.run(run())
