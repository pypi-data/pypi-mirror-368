"""Root namespace"""

from yarl import URL

from ..client import AbsolidixClient
from .base import BaseNamespace
from .calculations import AbsolidixCalculationsNamespace
from .stream import AbsolidixStreamNamespace
from .v0 import AbsolidixV0Namespace


class AbsolidixRootNamespace(BaseNamespace):
    """Root namespace"""

    def __init__(
        self,
        client: AbsolidixClient,
        base_url: URL,
        root: None = None,
        auth_req: bool = True,
    ) -> None:
        """Initialise the namespace."""
        super().__init__(client, base_url, root or self, auth_req)

    def __post_init__(self) -> None:
        self.__ns_calculations = AbsolidixCalculationsNamespace(
            self._client, self._base_url / "calculations", root=self
        )
        self.__ns_v0 = AbsolidixV0Namespace(
            self._client, self._base_url / "v0", root=self
        )
        self.__ns_stream = AbsolidixStreamNamespace(
            self._client, self._base_url / "stream", root=self
        )

    @property
    def calculations(self) -> "AbsolidixCalculationsNamespace":
        """Property to access the calculations namespace."""
        return self.__ns_calculations

    @property
    def v0(self) -> "AbsolidixV0Namespace":
        """Property to access the v0 namespace."""
        return self.__ns_v0

    @property
    def stream(self) -> "AbsolidixStreamNamespace":
        """Property to access the stream namespace."""
        return self.__ns_stream
