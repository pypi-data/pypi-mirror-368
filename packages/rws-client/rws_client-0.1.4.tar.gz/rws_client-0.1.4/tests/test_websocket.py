import asyncio

import pytest

from rws import ConnectionId, WebSocketClient


@pytest.mark.asyncio
async def test_websocket_connection() -> None:
    client = WebSocketClient()
    connected = False

    def on_open(connection_id: ConnectionId) -> None:
        nonlocal connected
        connected = True

    client.set_on_open(on_open)
    await client.connect("ws://43.207.106.154:5002", "test_conn")
    await asyncio.sleep(1)

    assert connected
    await client.close("test_conn")
