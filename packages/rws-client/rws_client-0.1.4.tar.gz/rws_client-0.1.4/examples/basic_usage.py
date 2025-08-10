import asyncio
import json
import threading

from rws import WebSocketClient


async def main():
    client = WebSocketClient()

    async def on_message(connection_id: str, message: str):
        print(f"收到消息 [{connection_id}]: {message}")

    async def on_open(connection_id: str):
        print(f"连接已打开 [{connection_id}]")
        await send_subscription(client, connection_id)
        await client.close("conn1")

    async def on_close(connection_id: str):
        # await asyncio.sleep(1)  # 确保在关闭连接前有足够的时间处理消息
        print(f"连接已关闭 [{connection_id}]")
        # client.stop()

    client.set_on_message(on_message)
    client.set_on_open(on_open)
    client.set_on_close(on_close)

    async def send_subscription(client, connection_id):
        req = {
            "event": "sub",
            "topic": "bbo.EXCHANGE_BINANCE.BTC-USDT.SECURITY_TYPE_PERP.CONTRACT_TYPE_LINEAR.USDT.UNSPECIFIED",
        }
        await client.send(json.dumps(req), connection_id)

    try:
        await client.run_forever("ws://52.199.185.117:5002/ws/dms", "conn1")
    finally:
        print("正在关闭连接...")
        try:
            # client.close("conn1")
            await asyncio.wait_for(client.close("conn1"), timeout=5.0)
        except asyncio.TimeoutError:
            print("关闭连接超时")
        print("已退出")


if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(main())).start()
