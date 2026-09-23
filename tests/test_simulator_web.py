import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from edge.simulator_web import SimulatorWeb


class DashboardTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = SimpleNamespace(read_telemetry=AsyncMock(return_value={'actual_active_power_kw':123}),
                                      read_active_configuration=AsyncMock(return_value={'q_setpoint_kvar':-100}))
        self.web = SimulatorWeb(SimpleNamespace(controller_client=self.client, device_id='coneza-sim-test',
            device_name='SIMULATION', last_sync_status={'status':'ONLINE'}))
        self.server = await asyncio.start_server(self.web.handle, '127.0.0.1', 0, limit=8192)

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def request(self, method, path):
        reader, writer = await asyncio.open_connection('127.0.0.1', self.server.sockets[0].getsockname()[1])
        writer.write(f'{method} {path} HTTP/1.1\r\nHost: localhost\r\n\r\n'.encode())
        await writer.drain()
        result = await reader.read()
        writer.close()
        await writer.wait_closed()
        return result

    async def test_status_contains_current_simulation_and_signed_config(self):
        response = await self.request('GET','/api/status')
        self.assertIn(b'200 OK', response)
        data = json.loads(response.split(b'\r\n\r\n',1)[1])
        self.assertEqual(data['configuration']['q_setpoint_kvar'], -100)
        self.assertEqual(data['telemetry']['actual_active_power_kw'],123)
        self.assertEqual(data['portal_status'],'ONLINE')

    async def test_read_only_and_unknown_routes(self):
        self.assertIn(b'405 Method Not Allowed', await self.request('POST','/api/status'))
        self.assertIn(b'404 Not Found', await self.request('GET','/anything'))
        self.client.read_telemetry.assert_not_awaited()

    async def test_failure_is_not_reported_as_live_data(self):
        self.client.read_telemetry.side_effect = OSError('private error')
        response = await self.request('GET','/api/status')
        self.assertIn(b'503 Service Unavailable',response)
        self.assertNotIn(b'private error',response)

    async def test_page_marks_simulation_and_prevents_caching(self):
        response = await self.request('GET','/')
        self.assertIn(b'SIMULATION',response)
        self.assertIn(b'Cache-Control: no-store',response)
        self.assertIn(b'frame-ancestors',response)


if __name__ == '__main__':
    unittest.main()
