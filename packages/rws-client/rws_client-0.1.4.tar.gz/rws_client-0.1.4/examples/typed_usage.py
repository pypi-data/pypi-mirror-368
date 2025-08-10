import asyncio
import json
import signal

from rws import ConnectionId, Message, WebSocketClient


async def main() -> None:
    client = WebSocketClient()

    async def on_message(connection_id: ConnectionId, message: Message) -> None:
        print(f"收到消息 [{connection_id}]: {message}")

    async def on_open(connection_id: ConnectionId) -> None:
        print(f"连接已打开 [{connection_id}]")
        await send_subscription(client, connection_id)

    def on_close(connection_id: ConnectionId) -> None:
        print(f"连接已关闭 [{connection_id}]")

    client.set_on_message(on_message)
    client.set_on_open(on_open)
    client.set_on_close(on_close)

    async def send_subscription(
        client: WebSocketClient, connection_id: ConnectionId
    ) -> None:
        req = {
            "event": "sub",
            "topic": "bbo.EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        }
        await client.send(json.dumps(req), connection_id)

    def signal_handler() -> None:
        print("\n正在优雅退出...")
        client.stop()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await client.run_forever("ws://43.207.106.154:5002/ws/dms", "conn1")
    finally:
        print("正在关闭连接...")
        try:
            await asyncio.wait_for(client.close("conn1"), timeout=5.0)
        except asyncio.TimeoutError:
            print("关闭连接超时")
        print("已退出")


if __name__ == "__main__":
    asyncio.run(main())
