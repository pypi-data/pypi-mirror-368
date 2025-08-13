"""Base of all namespaces"""

from __future__ import annotations

from typing import TYPE_CHECKING

from yarl import URL

from ..client import AbsolidixClient
from ..models.base import AbsolidixBase

if TYPE_CHECKING:  # pragma: no cover
    from .root import AbsolidixRootNamespace


class BaseNamespace(AbsolidixBase):
    """Used for the Absolidix API namespace."""

    _base_url: URL
    _client: AbsolidixClient
    _auth_required: bool = True
    _root: AbsolidixRootNamespace

    def __init__(
        self,
        client: AbsolidixClient,
        base_url: URL,
        root: AbsolidixRootNamespace,
        auth_req: bool = True,
    ) -> None:
        """Initialise the namespace."""
        self._client = client
        self._base_url = base_url
        self._auth_required = auth_req
        self._root = root
        self.__post_init__()

    def __post_init__(self) -> None:
        """Post initialisation."""
