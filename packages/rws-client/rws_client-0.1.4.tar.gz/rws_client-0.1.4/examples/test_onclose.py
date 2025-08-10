import asyncio
import json
from rws import WebSocketClient

async def test_on_close_callback():
    client = WebSocketClient()
    
    close_called = False
    
    async def on_message(connection_id: str, message: str):
        print(f"收到消息 [{connection_id}]: {message}")
        # 收到消息后关闭连接来触发on_close
        await client.close(connection_id)
    
    async def on_open(connection_id: str):
        print(f"连接已打开 [{connection_id}]")
        # 连接打开后发送一条测试消息
        await client.send("test message", connection_id)
        
    async def on_close(connection_id: str):
        global close_called
        close_called = True
        print(f"on_close回调被调用了！连接ID: {connection_id}")
        
    client.set_on_message(on_message)
    client.set_on_open(on_open)
    client.set_on_close(on_close)
    
    try:
        # 连接到一个工作的WebSocket服务器 
        print("尝试连接到WebSocket服务器...")
        await client.connect("ws://52.199.185.117:5002/ws/dms", "test_conn")
        
        # 等待消息处理
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"连接错误: {e}")
    finally:
        client.stop()
        print(f"测试结果 - on_close是否被调用: {close_called}")

if __name__ == "__main__":
    asyncio.run(test_on_close_callback())