"""
RWS (Rust WebSocket Client)
一个高性能的 WebSocket 客户端库，使用 Rust 实现核心功能。
"""

from .client import WebSocketClient
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

__all__ = [
    "WebSocketClient",
    "WebSocketClientProtocol",
    "OnMessageCallback",
    "AsyncOnMessageCallback",
    "OnOpenCallback",
    "AsyncOnOpenCallback",
    "OnCloseCallback",
    "AsyncOnCloseCallback",
    "ConnectionId",
    "Message",
    "WebSocketUrl",
] 