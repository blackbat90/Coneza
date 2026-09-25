"""Reject malformed job envelopes before any controller or HTTP access."""
import unittest
from unittest.mock import AsyncMock, Mock
from edge.backend_client import EdgeBackendClient


class JobValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_jobs_never_reach_controller(self):
        invalid = [None, [], 'job', {}, {'parameters': {}},
                   {'job_id': None, 'parameters': {}},
                   {'job_id': 1, 'parameters': {}},
                   {'job_id': '  ', 'parameters': {}},
                   {'job_id': 'job'}, {'job_id': 'job', 'parameters': None},
                   {'job_id': 'job', 'parameters': []},
                   {'job_id': 'job', 'parameters': 'config'}]
        for job in invalid:
            with self.subTest(job=job):
                gateway = EdgeBackendClient(device_id='test')
                gateway.controller_client.apply_configuration = AsyncMock()
                gateway._http_client = Mock()
                with self.assertRaises(ValueError):
                    await gateway._execute_pending_config(job)
                gateway.controller_client.apply_configuration.assert_not_awaited()
                gateway._http_client.assert_not_called()
