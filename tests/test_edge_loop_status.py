"""Unexpected heartbeat failures must invalidate displayed connectivity."""
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from edge.backend_client import EdgeBackendClient


class LoopStatusTests(unittest.IsolatedAsyncioTestCase):
    async def test_unexpected_failure_clears_online_and_loop_continues(self):
        gateway = EdgeBackendClient(device_id='test')
        gateway.register_device = AsyncMock()
        gateway.last_sync_status = {'status':'ONLINE', 'error':None}
        gateway.is_running = True
        calls = []

        async def heartbeat():
            calls.append(1)
            if len(calls) == 1:
                raise OSError('controller unavailable')
            gateway.is_running = False

        gateway.send_heartbeat = heartbeat
        with patch('edge.backend_client.asyncio.sleep', new_callable=AsyncMock), self.assertLogs('coneza_edge_client', level='ERROR'):
            await gateway._run_loop()
        self.assertEqual(len(calls), 2)
        self.assertEqual(gateway.last_sync_status['status'], 'HEARTBEAT_FAILED')

    async def test_cancellation_is_not_swallowed(self):
        gateway = EdgeBackendClient(device_id='test')
        gateway.register_device = AsyncMock()
        gateway.is_running = True
        gateway.send_heartbeat = AsyncMock(side_effect=asyncio.CancelledError)
        with self.assertRaises(asyncio.CancelledError):
            await gateway._run_loop()
