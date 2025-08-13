"""Calculations endpoints namespace"""

from collections.abc import Sequence

from ..helpers import absolidix_json_decoder, raise_on_absolidix_error
from .base import BaseNamespace


class AbsolidixCalculationsNamespace(BaseNamespace):
    """Calculations endpoints namespace"""

    @raise_on_absolidix_error
    async def supported(self) -> Sequence[str]:
        "Get supported calculation engines"
        async with await self._client.request(
            method="GET",
            url=self._base_url / "supported",
            auth_required=False,
        ) as resp:
            return await resp.json(loads=absolidix_json_decoder)
