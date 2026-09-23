import unittest
from unittest.mock import AsyncMock, Mock, patch

from edge.portal_tunnel import PortalRelay, pump
from edge.simulator_service import create_services


class PortalTransportTests(unittest.TestCase):
    def test_socket_mode_keeps_tls_verification_and_restricts_destination(self):
        config = {"CONEZA_BACKEND_URL": "https://coneza.de/portal",
                  "SIMULATOR_PORTAL_SOCKET": "/run/coneza-portal/portal.sock"}
        _, gateway = create_services(config)
        with patch("edge.simulator_service.httpx.AsyncHTTPTransport") as transport, patch(
            "edge.simulator_service.httpx.AsyncClient"
        ) as client:
            gateway._http_client(timeout=5)
            transport.assert_called_once_with(uds=config["SIMULATOR_PORTAL_SOCKET"], verify=True)
            client.assert_called_once_with(timeout=5, transport=transport.return_value, trust_env=False)
        for url in ("http://coneza.de", "https://192.168.1.10", "https://coneza.de:502"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                create_services({**config, "CONEZA_BACKEND_URL": url})


class PortalRelayTests(unittest.IsolatedAsyncioTestCase):
    async def test_pump_preserves_bytes(self):
        reader = Mock(read=AsyncMock(side_effect=[b"opaque TLS bytes", b""]))
        writer = Mock(drain=AsyncMock())
        await pump(reader, writer)
        writer.write.assert_called_once_with(b"opaque TLS bytes")
        writer.drain.assert_awaited_once()

    async def test_relay_connects_only_fixed_portal_and_cleans_up_failure(self):
        relay = PortalRelay()
        writer = Mock(wait_closed=AsyncMock())
        with patch("edge.portal_tunnel.asyncio.open_connection", new_callable=AsyncMock,
                   side_effect=OSError("unavailable")) as connect:
            await relay.handle(Mock(), writer)
        connect.assert_awaited_once_with("coneza.de", 443)
        writer.close.assert_called_once()
        self.assertEqual(relay.active, 0)

    async def test_connection_limit_rejects_without_upstream_access(self):
        relay = PortalRelay()
        relay.active = 16
        writer = Mock(wait_closed=AsyncMock())
        with patch("edge.portal_tunnel.asyncio.open_connection", new_callable=AsyncMock) as connect:
            await relay.handle(Mock(), writer)
        connect.assert_not_called()
        writer.close.assert_called_once()
