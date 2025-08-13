"Stream hub"

from asyncio import Event
from typing import TYPE_CHECKING, Set

from ..dtos import AbsolidixEventDTO
from .base import AbsolidixBase

if TYPE_CHECKING:  # pragma: no cover
    from .subscription import AbsolidixSubscription


class AbsolidixHub(AbsolidixBase):
    "Stream hub"

    _subscriptions: "Set[AbsolidixSubscription]"

    def __init__(self) -> None:
        self._subscriptions = set()
        self._connected_event = Event()

    def __len__(self) -> int:
        return len(self._subscriptions)

    @property
    def connected(self) -> bool:
        "Check if connected event is set"
        return self._connected_event.is_set()

    def set_connected(self) -> None:
        "Set connected event"
        self._connected_event.set()

    def set_disconnected(self) -> None:
        "Clear connected event"
        self._connected_event.clear()

    async def wait_connected(self) -> None:
        "Wait connected event"
        await self._connected_event.wait()

    def subscribe(self, subscription: "AbsolidixSubscription") -> None:
        "Register subscription"
        self._subscriptions.add(subscription)

    def unsubscribe(self, subscription: "AbsolidixSubscription") -> None:
        "Unsubscribe subscription"
        self._subscriptions.discard(subscription)

    def unsubscribe_all(self) -> None:
        "Unsubscribe all subscriptions"
        self._subscriptions.clear()

    async def close(self) -> None:
        "Close all subscriptions"
        subs = list(self._subscriptions)
        self.unsubscribe_all()
        for sub in subs:
            await sub.close()

    def publish(self, evt: AbsolidixEventDTO) -> None:
        "Publish message to subscriptions"
        for sub in self._subscriptions:
            sub.put_nowait(evt)
