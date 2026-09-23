"""Local Unix socket -> fixed public portal TLS port; never a general proxy.

Runs on the host as an unprivileged service. TLS remains end-to-end between
HTTPX inside the isolated container and coneza.de; this relay handles only bytes.
"""
import asyncio
import os
import signal

SOCKET_PATH = "/run/coneza-portal/portal.sock"
PORTAL_HOST = "coneza.de"
PORTAL_PORT = 443


async def pump(reader, writer):
    while True:
        data = await asyncio.wait_for(reader.read(65536), 60)
        if not data:
            return
        writer.write(data)
        await asyncio.wait_for(writer.drain(), 10)


class PortalRelay:
    def __init__(self):
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
            upstream_reader, upstream = await asyncio.wait_for(
                asyncio.open_connection(PORTAL_HOST, PORTAL_PORT), 10
            )
            tasks = [asyncio.create_task(pump(reader, upstream)),
                     asyncio.create_task(pump(upstream_reader, writer))]
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


async def main():
    relay = PortalRelay()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stop.set)
    server = await asyncio.start_unix_server(relay.handle, SOCKET_PATH)
    # Only grants local access to this fixed public endpoint, not host networking.
    os.chmod(SOCKET_PATH, 0o666)
    async with server:
        await stop.wait()


if __name__ == "__main__":
    asyncio.run(main())
