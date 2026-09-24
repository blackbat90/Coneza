"""Local mocks only: rejected result reports must not be logged as delivered."""
import unittest
from unittest.mock import AsyncMock, patch
import httpx
from edge.backend_client import EdgeBackendClient


class ResultReportingTests(unittest.IsolatedAsyncioTestCase):
    async def test_delivery_log_requires_http_success(self):
        for code in (200, 204, 307, 401, 500):
            with self.subTest(code=code):
                gateway = EdgeBackendClient(device_id='test')
                gateway.controller_client.apply_configuration = AsyncMock(return_value={
                    'success': True, 'verification_log': [], 'registers_updated': 1})
                with patch.object(gateway, '_http_client', side_effect=lambda **kw: httpx.AsyncClient(
                    transport=httpx.MockTransport(lambda request: httpx.Response(code)), **kw)
                ), self.assertLogs('coneza_edge_client', level='INFO') as logs:
                    await gateway._execute_pending_config({'job_id':'test-job', 'parameters':{}})
                output = '\n'.join(logs.output)
                if code < 300:
                    self.assertIn('Reported config job', output)
                else:
                    self.assertNotIn('Reported config job', output)
                    self.assertIn('Failed to report config job', output)
                gateway.controller_client.apply_configuration.assert_awaited_once()
