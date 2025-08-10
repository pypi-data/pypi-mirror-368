import asyncio

from rws import WebSocketClient


close_called = False

async def test_explicit_close():
    global close_called
    client = WebSocketClient()

    def on_close(connection_id: str):
        global close_called
        close_called = True
        print(f"on_close回调被调用了！连接ID: {connection_id}")

    client.set_on_close(on_close)

    try:
        print("尝试连接...")
        await client.connect("ws://52.199.185.117:5002/ws/dms", "test_conn")
        print("连接成功，等待1秒后关闭...")
        await asyncio.sleep(1)

        print("显式关闭连接...")
        await client.close("test_conn")

        print("等待回调执行...")
        await asyncio.sleep(1)

    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.stop()
        print(f"测试结果 - on_close是否被调用: {close_called}")


if __name__ == "__main__":
    asyncio.run(test_explicit_close())
