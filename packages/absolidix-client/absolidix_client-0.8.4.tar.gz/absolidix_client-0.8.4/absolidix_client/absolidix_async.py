"""Main Absolidix API async client"""

from types import TracebackType
from typing import Literal, Optional, Union

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TraceConfig
from aiohttp.hdrs import USER_AGENT
from aiohttp.typedefs import LooseHeaders, StrOrURL
from yarl import URL

from .client import AbsolidixClient
from .compat import NotRequired, TypedDict, Unpack
from .const import DEFAULT_USER_AGENT
from .models import AbsolidixBase, BaseAuthenticator
from .namespaces.calculations import AbsolidixCalculationsNamespace
from .namespaces.root import AbsolidixRootNamespace
from .namespaces.stream import AbsolidixStreamNamespace
from .namespaces.v0 import AbsolidixV0Namespace


class AbsolidixAPIKwargs(TypedDict):
    "AbsolidixAPI init kwargs"

    auth: BaseAuthenticator
    headers: NotRequired[LooseHeaders]
    timeout: NotRequired[Union[float, Literal[False], None]]
    client_name: NotRequired[str]
    trace_configs: NotRequired[list[TraceConfig]]


class AbsolidixAPIAsync(AbsolidixBase):
    """Main Absolidix API async client"""

    _close_session = False
    _session: aiohttp.ClientSession

    def __init__(
        self,
        base_url: StrOrURL,
        session: Optional[ClientSession] = None,
        **opts: Unpack[AbsolidixAPIKwargs],
    ):
        """
        Initialize async Absolidix client.

        **Arguments**:

        `bese_url`
        URL of Absolidix BFF server. `str` or `yarl.URL`.

        `session` (Optional)
        `aiohttp.ClientSession` to be used by this package.
        If you do not pass one, one will be created for you.

        `headers` (Optional)
        Optional dictionary of always sent headers. Used if `session` is omitted.

        `timeout` (Optional)
        Optional float timeout in seconds. None if not timeout. False if not set.
        Used as `aiohttp` timeout if `session` is omitted.

        `client_name` (Optional)
        Optional string for user agent.
        Used if `session` is omitted.
        """
        headers = opts.get("headers")
        if session is None:
            timeout = opts.get("timeout", None)
            session = aiohttp.ClientSession(
                timeout=(
                    timeout
                    if isinstance(timeout, ClientTimeout)
                    else ClientTimeout(total=timeout or None)
                ),
                headers=headers,
                trace_configs=opts.get("trace_configs"),
            )
            session.headers[USER_AGENT] = opts.get("client_name", DEFAULT_USER_AGENT)
            self._close_session = True
        self._session = session

        base_url = URL(base_url)
        if not base_url.is_absolute():
            raise TypeError("Base URL should be absolute")
        client = AbsolidixClient(session, base_url, opts["auth"])
        self._ns_root = AbsolidixRootNamespace(client, base_url)

    @property
    def calculations(
        self,
    ) -> AbsolidixCalculationsNamespace:
        """Property to access the calculations namespace."""
        return self._ns_root.calculations

    @property
    def v0(self) -> AbsolidixV0Namespace:
        """Property to access the v0 namespace."""
        return self._ns_root.v0

    @property
    def stream(self) -> AbsolidixStreamNamespace:
        """Property to access the stream namespace."""
        return self._ns_root.stream

    async def __aenter__(self) -> "AbsolidixAPIAsync":
        """Async enter."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        "Close stream and http session"
        self.stream.close()
        if self._session and self._close_session:
            await self._session.close()
