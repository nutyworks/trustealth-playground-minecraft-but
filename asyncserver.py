#!/usr/bin/python3.9

import asyncio
from asyncio.streams import StreamReader, StreamWriter
from connection import Connection
from io import BytesIO

connections = {}

async def handle_connection(reader: StreamReader, writer: StreamWriter):

    addr = writer.get_extra_info('peername')
    connections[addr] = Connection(addr)

    data = None

    while True:
        while True:
            data = await reader.read(100)

            if data:
                break

        print(f"Received {data!r} from {addr!r}")
        response, disconnect = None, True
        try:
            response, disconnect = connections[addr].decode_and_response(BytesIO(data))
        except EOFError:
            writer.close()
            await writer.wait_closed()
        except OSError:
            writer.close()
            await writer.wait_closed()

        if response:
            print(f"Sent {response!r} to {addr!r}")
            writer.write(response)
            await writer.drain()

        if disconnect:
            break 

    print("Close the connection")
    writer.close()
    await writer.wait_closed()

    del connections[addr]


async def main():
    server = await asyncio.start_server(
        handle_connection, '127.0.0.1', 25565)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())