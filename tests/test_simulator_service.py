"""EEP-77: local-only simulator and mocked portal; no external services."""
import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch

import httpx

from edge.simulator_service import create_services, run


class SimulatorIdentityTests(unittest.TestCase):
    def test_identity_and_controller_are_simulator_only(self):
        simulator, gateway = create_services({
            "CONEZA_BACKEND_URL": "https://portal.invalid/portal/",
            "EZA_CONTROLLER_HOST": "192.0.2.55", "EZA_CONTROLLER_PORT": "502",
        })
        self.assertEqual(simulator.host, "127.0.0.1")
        self.assertEqual(gateway.controller_client.host, "127.0.0.1")
        self.assertEqual(gateway.controller_client.port, 5502)
        self.assertEqual(gateway.backend_url, "https://portal.invalid/portal")
        self.assertTrue(gateway.device_id.startswith("coneza-sim-"))
        self.assertTrue(gateway.device_name.startswith("SIMULATION - "))

    def test_invalid_identity_and_backend_fail_before_startup(self):
        for url in ("", "file:///tmp/data", "https://user:secret@portal.invalid", "https://portal.invalid?token=secret"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                create_services({"CONEZA_BACKEND_URL": url})
        with self.assertRaises(ValueError):
            create_services({"CONEZA_BACKEND_URL": "https://portal.invalid", "SIMULATOR_DEVICE_ID": "physical-gateway"})


class SimulatorPortalTests(unittest.IsolatedAsyncioTestCase):
    async def test_registration_telemetry_and_simulated_deployment(self):
        simulator, gateway = create_services({"CONEZA_BACKEND_URL": "https://portal.invalid/portal"})
        simulator.port = 0  # Isolated OS-assigned loopback port, never a real PLC.
        await simulator.start()
        gateway.controller_client.port = simulator.server.sockets[0].getsockname()[1]
        requests = []

        def portal(request):
            self.assertEqual(request.url.host, "portal.invalid")
            body = json.loads(request.content)
            requests.append((request.url.path, body))
            if request.url.path.endswith("/heartbeat"):
                return httpx.Response(200, json={"pending_configuration": {
                    "job_id": "simulated-job", "parameters": {
                        "p_setpoint_kw": 1234, "q_setpoint_kvar": -100,
                        "q_u_curve": {"q4_percent": -100},
                    },
                }})
            return httpx.Response(200, json={})

        client_type = httpx.AsyncClient
        try:
            with patch("edge.backend_client.httpx.AsyncClient", side_effect=lambda **kwargs: client_type(
                transport=httpx.MockTransport(portal), **kwargs
            )), patch.object(gateway, "get_local_ip", return_value="127.0.0.1"):
                self.assertTrue(await gateway.register_device())
                await gateway.send_heartbeat()
            self.assertEqual(len(requests), 3)
            self.assertIn("SIMULATION", requests[0][1]["name"])
            self.assertTrue(requests[1][1]["controller_connected"])
            self.assertIn("actual_active_power_kw", requests[1][1]["telemetry"])
            self.assertTrue(requests[2][1]["success"])
            actual = await gateway.controller_client.read_active_configuration()
            self.assertEqual(actual["p_setpoint_kw"], 1234)
            self.assertEqual(actual["q_setpoint_kvar"], -100)
            self.assertEqual(actual["q_u_curve"]["q4_percent"], -100)
        finally:
            await simulator.stop()

    async def test_shutdown_stops_gateway_and_simulator(self):
        simulator, gateway = create_services({"CONEZA_BACKEND_URL": "https://portal.invalid"})
        stop = asyncio.Event()
        stop.set()
        with patch("edge.simulator_service.create_services", return_value=(simulator, gateway)), patch.object(
            simulator, "start", new_callable=AsyncMock
        ), patch.object(simulator, "stop", new_callable=AsyncMock) as stop_sim, patch.object(
            gateway, "start"
        ) as start_gateway, patch.object(gateway, "stop", new_callable=AsyncMock) as stop_gateway:
            await run(stop)
            start_gateway.assert_called_once()
            stop_gateway.assert_awaited_once()
            stop_sim.assert_awaited_once()
