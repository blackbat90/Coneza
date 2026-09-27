"""Telemetry read failure must not publish a healthy controller state."""
import json
import unittest
from unittest.mock import AsyncMock, patch
import httpx
from edge.backend_client import EdgeBackendClient


class TelemetryFailureTests(unittest.IsolatedAsyncioTestCase):
    async def test_failure_then_recovery(self):
        gateway = EdgeBackendClient(device_id='test')
        gateway.controller_client.test_connection = AsyncMock(return_value={
            'connected': True, 'controller_state': 'ONLINE_REGULATING'})
        gateway.controller_client.read_telemetry = AsyncMock(side_effect=[
            OSError('read failed'), {'actual_active_power_kw': 100}])
        payloads = []

        def response(request):
            payloads.append(json.loads(request.content))
            return httpx.Response(200, json={})

        with patch.object(gateway, 'get_local_ip', return_value='127.0.0.1'), patch.object(
            gateway, '_http_client', side_effect=lambda **kw: httpx.AsyncClient(
                transport=httpx.MockTransport(response), **kw)
        ), self.assertLogs('coneza_edge_client', level='WARNING'):
            await gateway.send_heartbeat()
            await gateway.send_heartbeat()
        self.assertFalse(payloads[0]['controller_connected'])
        self.assertEqual(payloads[0]['controller_state'], 'TELEMETRY_UNAVAILABLE')
        self.assertEqual(payloads[0]['telemetry'], {})
        self.assertTrue(payloads[1]['controller_connected'])
        self.assertEqual(payloads[1]['telemetry']['actual_active_power_kw'], 100)
        self.assertEqual(gateway.last_sync_status['status'], 'ONLINE')
