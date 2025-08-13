"""v0 namespace"""

from .base import BaseNamespace
from .v0_auth import AbsolidixV0AuthNamespace
from .v0_calculations import AbsolidixV0CalculationsNamespace
from .v0_collections import AbsolidixV0CollectionsNamespace
from .v0_datasources import AbsolidixV0DatasourcesNamespace


class AbsolidixV0Namespace(BaseNamespace):
    """v0 namespace"""

    def __post_init__(self) -> None:
        self.__ns_auth = AbsolidixV0AuthNamespace(
            self._client, self._base_url / "auth", root=self._root
        )
        self.__ns_calculations = AbsolidixV0CalculationsNamespace(
            self._client, self._base_url / "calculations", root=self._root
        )
        self.__ns_collections = AbsolidixV0CollectionsNamespace(
            self._client, self._base_url / "collections", root=self._root
        )
        self.__ns_datasources = AbsolidixV0DatasourcesNamespace(
            self._client, self._base_url / "datasources", root=self._root
        )

    async def ping(self) -> None:
        "Run ping pong game"
        await self._client.request(url=self._base_url, method="HEAD", json={})

    @property
    def auth(self) -> AbsolidixV0AuthNamespace:
        "Property to access the auth namespace."
        return self.__ns_auth

    @property
    def calculations(self) -> AbsolidixV0CalculationsNamespace:
        "Property to access the calculations namespace."
        return self.__ns_calculations

    @property
    def collections(self) -> AbsolidixV0CollectionsNamespace:
        "Property to access the collections namespace."
        return self.__ns_collections

    @property
    def datasources(self) -> AbsolidixV0DatasourcesNamespace:
        "Property to access the datasources namespace."
        return self.__ns_datasources
