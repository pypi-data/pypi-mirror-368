"Stream subscription"

from asyncio import CancelledError, Queue, QueueFull
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from types import TracebackType
from typing import TYPE_CHECKING, Optional

from ..dtos import AbsolidixEventDTO, AbsolidixRequestIdDTO
from ..helpers import raise_on_absolidix_error_in_event
from .base import AbsolidixBase

if TYPE_CHECKING:  # pragma: no cover
    from .hub import AbsolidixHub

SubscribeCallable = Callable[[], "AbsolidixSubscription"]
RequestIdCallable = Callable[[], Awaitable[AbsolidixRequestIdDTO]]


@raise_on_absolidix_error_in_event
async def act_and_get_result_from_stream(
    sub_func: SubscribeCallable, func: RequestIdCallable
) -> AbsolidixEventDTO:
    "Do a request and get response from stream"
    async with sub_func() as sub:
        resp = await func()
        async for msg in sub:
            data = msg.get("data")
            if isinstance(data, dict) and data.get("req_id") == resp.get("req_id"):
                return msg
    raise CancelledError  # pragma: no cover


class AbsolidixSubscription(AbsolidixBase):
    "Message subscription"

    hub: "AbsolidixHub"
    queue: "Queue[AbsolidixEventDTO]"

    def __init__(
        self,
        hub: "AbsolidixHub",
        predicate: Optional[Callable[[AbsolidixEventDTO], bool]] = None,
        queue_size: int = 0,
    ) -> None:
        self.hub = hub
        self.queue = Queue(maxsize=queue_size)
        self._predicate = predicate

    def put_nowait(self, message: AbsolidixEventDTO) -> None:
        "Put message to query without wait"
        try:
            if self._predicate is None or self._predicate(message):
                self.queue.put_nowait(message)
        except QueueFull:
            self.logger.warning("Subscription's queue is full")

    async def close(self) -> None:
        "Close subscription and join message queue"
        self.hub.unsubscribe(self)
        await self.queue.join()

    def __len__(self) -> int:
        return self.queue.qsize()

    async def __aenter__(self) -> "AbsolidixSubscription":
        self.hub.subscribe(self)
        await self.hub.wait_connected()
        return self.__aiter__()

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.hub.unsubscribe(self)

    def __aiter__(self) -> "AbsolidixSubscription":
        return self

    @asynccontextmanager
    async def _cm(self):
        yield await self.queue.get()

    async def __anext__(self) -> AbsolidixEventDTO:
        async with self._cm() as msg:
            return msg
