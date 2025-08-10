from typing import Callable, Protocol, Union
from typing import Awaitable
from typing_extensions import TypeAlias

# 类型别名
ConnectionId: TypeAlias = str
Message: TypeAlias = str
Topic: TypeAlias = str
WebSocketUrl: TypeAlias = str

# 回调函数类型
OnMessageCallback: TypeAlias = Callable[[ConnectionId, Message], None]
OnOpenCallback: TypeAlias = Callable[[ConnectionId], None]
OnCloseCallback: TypeAlias = Callable[[ConnectionId], None]

# 异步回调函数类型
AsyncOnMessageCallback: TypeAlias = Callable[
    [ConnectionId, Message], Union[None, "Awaitable[None]"]
]
AsyncOnOpenCallback: TypeAlias = Callable[
    [ConnectionId], Union[None, "Awaitable[None]"]
]
AsyncOnCloseCallback: TypeAlias = Callable[
    [ConnectionId], Union[None, "Awaitable[None]"]
]


# 协议定义
class WebSocketClientProtocol(Protocol):
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
