"""Heartbeat state regressions; all controller and HTTP calls are mocked."""
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from edge.backend_client import EdgeBackendClient


class HeartbeatStatusTests(unittest.IsolatedAsyncioTestCase):
    async def test_http_rejection_clears_online_and_recovers(self):
        for code in (301, 400, 401, 403, 429, 500, 503):
            with self.subTest(code=code):
                gateway = EdgeBackendClient(device_id='test')
                gateway.controller_client.test_connection = AsyncMock(return_value={'connected': False})
                gateway._execute_pending_config = AsyncMock()
                replies = iter([httpx.Response(code, text='private response body'), httpx.Response(200, json={})])
                transport = httpx.MockTransport(lambda request: next(replies))
                with patch.object(gateway, 'get_local_ip', return_value='127.0.0.1'), patch.object(
                    gateway, '_http_client', side_effect=lambda **kw: httpx.AsyncClient(transport=transport, **kw)
                ):
                    gateway.last_sync_status = {'status':'ONLINE', 'error':None}
                    await gateway.send_heartbeat()
                    self.assertEqual(gateway.last_sync_status, {'status':'HEARTBEAT_FAILED', 'error':f'HTTP {code}'})
                    gateway._execute_pending_config.assert_not_awaited()
                    await gateway.send_heartbeat()
                    self.assertEqual(gateway.last_sync_status, {'status':'ONLINE', 'error':None})

    async def test_missing_device_still_registers(self):
        gateway = EdgeBackendClient(device_id='test')
        gateway.controller_client.test_connection = AsyncMock(return_value={'connected':False})
        gateway.register_device = AsyncMock(return_value=True)
        with patch.object(gateway, 'get_local_ip', return_value='127.0.0.1'), patch.object(
            gateway, '_http_client', side_effect=lambda **kw: httpx.AsyncClient(
                transport=httpx.MockTransport(lambda request: httpx.Response(404)), **kw)
        ):
            await gateway.send_heartbeat()
        gateway.register_device.assert_awaited_once()
