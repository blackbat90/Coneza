import asyncio
import unittest
from edge.modbus_access import Relay


class RelayTests(unittest.IsolatedAsyncioTestCase):
    async def test_fragmented_binary_data_and_cleanup(self):
        async def echo(reader, writer):
            try:
                while data := await reader.read(1024):
                    writer.write(data)
                    await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()
        upstream = await asyncio.start_server(echo, '127.0.0.1', 0)
        relay = Relay(lambda: asyncio.open_connection('127.0.0.1', upstream.sockets[0].getsockname()[1]))
        server = await asyncio.start_server(relay.handle, '127.0.0.1', 0)
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', server.sockets[0].getsockname()[1])
            packet = bytes.fromhex('000100000006010300000001')
            for chunk in (packet[:3], packet[3:]):
                writer.write(chunk)
                await writer.drain()
                self.assertEqual(await asyncio.wait_for(reader.readexactly(len(chunk)), 2), chunk)
            writer.close()
            await writer.wait_closed()
            for _ in range(100):
                if relay.active == 0:
                    break
                await asyncio.sleep(.01)
            self.assertEqual(relay.active, 0)
        finally:
            server.close()
            upstream.close()
            await server.wait_closed()
            await upstream.wait_closed()

    async def test_unavailable_target_closes_connection(self):
        async def unavailable():
            raise OSError('unreachable')
        relay = Relay(unavailable)
        server = await asyncio.start_server(relay.handle, '127.0.0.1', 0)
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', server.sockets[0].getsockname()[1])
            self.assertEqual(await asyncio.wait_for(reader.read(), 2), b'')
            writer.close()
            await writer.wait_closed()
        finally:
            server.close()
            await server.wait_closed()
