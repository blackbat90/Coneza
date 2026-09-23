"""Expose only the simulator dashboard socket on the IPC LAN address."""
import asyncio
from edge.portal_tunnel import pump


class WebRelay:
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
            remote, upstream = await asyncio.wait_for(asyncio.open_unix_connection('/run/coneza-simulator-web/web.sock'), 3)
            tasks = [asyncio.create_task(pump(reader, upstream)), asyncio.create_task(pump(remote, writer))]
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        except (OSError, asyncio.TimeoutError):
            writer.write(b'HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\nContent-Length: 21\r\n\r\nSimulator unavailable')
            await writer.drain()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            for stream in (writer, upstream):
                if stream:
                    stream.close()
                    await stream.wait_closed()
            self.active -= 1


async def main():
    server = await asyncio.start_server(WebRelay().handle, '192.168.8.186', 80)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
