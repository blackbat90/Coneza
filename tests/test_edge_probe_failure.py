"""Controller probing must not suppress portal availability reporting."""
import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch
import httpx
from edge.backend_client import EdgeBackendClient


class ProbeFailureTests(unittest.IsolatedAsyncioTestCase):
    async def test_probe_failure_is_reported_and_recovers(self):
        gateway = EdgeBackendClient(device_id='test')
        gateway.controller_client.test_connection = AsyncMock(side_effect=[
            OSError('private transport detail'), {'connected': True, 'controller_state': 'RUNNING'}])
        gateway.controller_client.read_telemetry = AsyncMock(return_value={'actual_active_power_kw': 42})
        payloads = []

        def response(request):
            payloads.append(json.loads(request.content))
            return httpx.Response(200, json={})

        with patch.object(gateway, 'get_local_ip', return_value='127.0.0.1'), patch.object(
            gateway, '_http_client', side_effect=lambda **kw: httpx.AsyncClient(
                transport=httpx.MockTransport(response), **kw)
        ):
            await gateway.send_heartbeat()
            gateway.controller_client.read_telemetry.assert_not_awaited()
            await gateway.send_heartbeat()
        self.assertEqual(payloads[0]['controller_state'], 'CONNECTION_CHECK_FAILED')
        self.assertFalse(payloads[0]['controller_connected'])
        self.assertEqual(payloads[0]['telemetry'], {})
        self.assertNotIn('private transport detail', json.dumps(payloads))
        self.assertTrue(payloads[1]['controller_connected'])
        self.assertEqual(payloads[1]['telemetry']['actual_active_power_kw'], 42)

    async def test_cancellation_does_not_send_heartbeat(self):
        gateway = EdgeBackendClient(device_id='test')
        gateway.controller_client.test_connection = AsyncMock(side_effect=asyncio.CancelledError)
        with patch.object(gateway, '_http_client') as client, self.assertRaises(asyncio.CancelledError):
            await gateway.send_heartbeat()
        client.assert_not_called()
