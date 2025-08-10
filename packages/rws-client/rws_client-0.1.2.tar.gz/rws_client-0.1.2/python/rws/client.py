from typing import Union

from .typing import (
    AsyncOnCloseCallback,
    AsyncOnMessageCallback,
    AsyncOnOpenCallback,
    ConnectionId,
    Message,
    OnCloseCallback,
    OnMessageCallback,
    OnOpenCallback,
    WebSocketClientProtocol,
    WebSocketUrl,
)

# 直接从 _rws 模块导入
try:
    from ._rws import WebSocketClient as _WebSocketClient  # type: ignore
except ImportError:
    # 如果在开发环境中，可能需要从不同的路径导入
    try:
        from _rws import WebSocketClient as _WebSocketClient  # type: ignore
    except ImportError:
        raise ImportError(
            "无法导入 WebSocketClient。请确保已经正确编译 Rust 扩展。\n"
            "尝试运行: poetry run maturin develop"
        )


class WebSocketClient(WebSocketClientProtocol):
    """WebSocket客户端的Python包装类，提供类型安全的API"""

    def __init__(self) -> None:
        """初始化WebSocket客户端"""
        self._client: _WebSocketClient = _WebSocketClient()

    def set_on_message(
        self, callback: Union[OnMessageCallback, AsyncOnMessageCallback]
    ) -> None:
        """设置消息回调函数"""
        self._client.set_on_message(callback)

    def set_on_open(self, callback: Union[OnOpenCallback, AsyncOnOpenCallback]) -> None:
        """设置连接打开回调函数"""
        self._client.set_on_open(callback)

    def set_on_close(
        self, callback: Union[OnCloseCallback, AsyncOnCloseCallback]
    ) -> None:
        """设置连接关闭回调函数"""
        self._client.set_on_close(callback)

    async def connect(self, url: WebSocketUrl, connection_id: ConnectionId) -> None:
        """连接到WebSocket服务器"""
        await self._client.connect(url, connection_id)

    async def send(self, message: Message, connection_id: ConnectionId) -> None:
        """发送消息"""
        await self._client.send(message, connection_id)

    def sync_send(self, message: Message, connection_id: ConnectionId) -> None:
        """发送消息"""
        self._client.send(message, connection_id)

    async def close(self, connection_id: ConnectionId) -> None:
        """关闭连接"""
        await self._client.close(connection_id)

    def stop(self) -> None:
        """停止客户端"""
        self._client.stop()

    async def run_forever(self, url: WebSocketUrl, connection_id: ConnectionId) -> None:
        """永久运行模式"""
        await self._client.run_forever(url, connection_id)
