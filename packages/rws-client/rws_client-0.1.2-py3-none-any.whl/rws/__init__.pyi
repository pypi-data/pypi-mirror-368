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

class WebSocketClient(WebSocketClientProtocol):
    def __init__(self) -> None: ...
    def set_on_message(
        self, callback: Union[OnMessageCallback, AsyncOnMessageCallback]
    ) -> None: ...
    def set_on_open(
        self, callback: Union[OnOpenCallback, AsyncOnOpenCallback]
    ) -> None: ...
    def set_on_close(
        self, callback: Union[OnCloseCallback, AsyncOnCloseCallback]
    ) -> None: ...
    async def connect(self, url: WebSocketUrl, connection_id: ConnectionId) -> None: ...
    async def send(self, message: Message, connection_id: ConnectionId) -> None: ...
    async def close(self, connection_id: ConnectionId) -> None: ...
    def stop(self) -> None: ...
    async def run_forever(
        self, url: WebSocketUrl, connection_id: ConnectionId
    ) -> None: ... 