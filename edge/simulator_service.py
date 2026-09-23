"""Standalone, simulator-only portal gateway. Not a certified PCU implementation."""
import asyncio
import logging
import os
import re
import signal
import httpx
from urllib.parse import urlsplit

from edge.backend_client import EdgeBackendClient
from edge.phoenix_eza.simulator import PhoenixEZASimulator


class SimulatorGateway(EdgeBackendClient):
    portal_socket = None

    def _http_client(self, **kwargs):
        if self.portal_socket:
            kwargs["transport"] = httpx.AsyncHTTPTransport(uds=self.portal_socket, verify=True)
            kwargs["trust_env"] = False
        return httpx.AsyncClient(**kwargs)


def create_services(environ=None):
    env = os.environ if environ is None else environ
    url = env.get("CONEZA_BACKEND_URL", "").rstrip("/")
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("CONEZA_BACKEND_URL must be an HTTP(S) base URL without credentials, query or fragment")
    portal_socket = env.get("SIMULATOR_PORTAL_SOCKET")
    if portal_socket and (parsed.scheme != "https" or parsed.hostname != "coneza.de" or parsed.port not in (None, 443)):
        raise ValueError("Portal socket mode only supports https://coneza.de on port 443")
    device_id = env.get("SIMULATOR_DEVICE_ID", "coneza-sim-01")
    if not re.fullmatch(r"coneza-sim-[a-zA-Z0-9_-]{1,64}", device_id):
        raise ValueError("SIMULATOR_DEVICE_ID must start with coneza-sim- and have a short alphanumeric suffix")
    name = env.get("SIMULATOR_NAME", "Ubuntu IPC virtual EZA")
    # Never read EZA_CONTROLLER_HOST/PORT: deployments can only reach this container's simulator.
    simulator = PhoenixEZASimulator(host="127.0.0.1", port=5502)
    gateway = SimulatorGateway(
        backend_url=url, device_id=device_id, device_name=f"SIMULATION - {name}",
        controller_host="127.0.0.1", controller_port=5502,
    )
    gateway.portal_socket = portal_socket
    return simulator, gateway


async def run(stop_event=None):
    simulator, gateway = create_services()
    stop = stop_event or asyncio.Event()
    loop = asyncio.get_running_loop()
    installed = []
    if stop_event is None:
        for signum in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(signum, stop.set)
            installed.append(signum)
    try:
        await simulator.start()
        gateway.start()
        logging.info("Simulator started as %s; all controller traffic stays on loopback", gateway.device_id)
        await stop.wait()
    finally:
        await gateway.stop()
        await simulator.stop()
        for signum in installed:
            loop.remove_signal_handler(signum)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
