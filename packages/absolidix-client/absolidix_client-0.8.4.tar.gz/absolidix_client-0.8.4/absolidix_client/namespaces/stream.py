"""Stream endpoint namespace"""

import asyncio
from collections.abc import Callable
from typing import NoReturn, Optional

from aiohttp_sse_client.client import MessageEvent

from ..dtos import AbsolidixEventDTO
from ..models import AbsolidixHub, AbsolidixMessageEvent, AbsolidixSubscription
from .base import BaseNamespace


class AbsolidixStreamNamespace(BaseNamespace):
    """Stream endpoints namespace"""

    _hub: AbsolidixHub
    _stream_task: Optional[asyncio.Task[NoReturn]] = None
    _sse_client_task: Optional[asyncio.Task[None]] = None
    _subscribe_event: asyncio.Event

    def __post_init__(self) -> None:
        self._hub = AbsolidixHub()
        self._stream_task = asyncio.create_task(
            self._stream_consumer(), name="StreamConsumerTask"
        )
        self._subscribe_event = asyncio.Event()
        return super().__post_init__()

    async def _stream_consumer(self):
        def on_open():
            self._hub.set_connected()

        def on_message(evt: MessageEvent):
            self._hub.set_connected()
            evt_dto = AbsolidixMessageEvent.from_dto(evt).to_dto()
            self._hub.publish(evt_dto)
            # cancel streaming task if no subscribers
            if self._sse_client_task and len(self._hub) == 0:
                self._hub.set_disconnected()
                self._sse_client_task.cancel()

        while True:
            await self._subscribe_event.wait()
            if self._sse_client_task is None or self._sse_client_task.done():
                self._sse_client_task = asyncio.create_task(
                    self._client.sse(self._base_url, on_message, on_open),
                    name="SSEClientTask",
                )
            self._subscribe_event.clear()
            while not self._hub.connected:
                await asyncio.sleep(0.1)
                await self._root.v0.ping()

    def close(self):
        "Close background stream consumer"
        if self._stream_task:
            self._stream_task.cancel()
        if self._sse_client_task:
            self._sse_client_task.cancel()

    def subscribe(
        self, predicate: Optional[Callable[[AbsolidixEventDTO], bool]] = None
    ):
        "Subscribe to stream"
        self._subscribe_event.set()
        return AbsolidixSubscription(self._hub, predicate=predicate)
