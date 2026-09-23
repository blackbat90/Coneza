"""Fixed Modbus relays: LAN 502 -> physical PCU; LAN 5502 -> isolated simulator."""
import asyncio
import os
import sys

SOCKET = '/run/coneza-simulator-web/modbus.sock'


async def pump(reader, writer):
    while True:
        data = await asyncio.wait_for(reader.read(65536), 60)
        if not data:
            return
        writer.write(data)
        await asyncio.wait_for(writer.drain(), 10)


class Relay:
    def __init__(self, connect):
        self.connect = connect
        self.active = 0

    async def handle(self, reader, writer):
        if self.active >= 16:
            writer.close()
            await writer.wait_closed()
            return
        self.active += 1
        upstream = None
        tasks = []
        try:
            remote, upstream = await asyncio.wait_for(self.connect(), 5)
            tasks = [asyncio.create_task(pump(reader, upstream)),
                     asyncio.create_task(pump(remote, writer))]
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        except (OSError, asyncio.TimeoutError):
            pass
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            for stream in (writer, upstream):
                if stream:
                    stream.close()
                    try:
                        await stream.wait_closed()
                    except OSError:
                        pass
            self.active -= 1


async def host():
    physical = Relay(lambda: asyncio.open_connection('192.168.1.10', 502))
    simulator = Relay(lambda: asyncio.open_unix_connection(SOCKET))
    real_server = await asyncio.start_server(physical.handle, '192.168.8.186', 502)
    try:
        sim_server = await asyncio.start_server(simulator.handle, '192.168.8.186', 5502)
        async with real_server, sim_server:
            await asyncio.gather(real_server.serve_forever(), sim_server.serve_forever())
    finally:
        real_server.close()
        await real_server.wait_closed()


async def container():
    from edge.simulator_service import run
    relay = Relay(lambda: asyncio.open_connection('127.0.0.1', 5502))
    server = await asyncio.start_unix_server(relay.handle, SOCKET)
    os.chmod(SOCKET, 0o666)
    async with server:
        await run()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    if sys.argv[1:] == ['container']:
        asyncio.run(container())
    elif sys.argv[1:] == ['host']:
        asyncio.run(host())
    else:
        raise SystemExit('Expected host or container')
