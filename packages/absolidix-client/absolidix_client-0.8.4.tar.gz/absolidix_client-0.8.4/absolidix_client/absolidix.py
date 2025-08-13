"""Absolidix API synchronous client"""

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from typing import Any, Literal, Optional, TypeVar, Union, cast
from warnings import warn

from aiohttp.typedefs import StrOrURL

from absolidix_client.dtos.datasource import AbsolidixDataSourceDTO

from .absolidix_async import AbsolidixAPIAsync, AbsolidixAPIKwargs
from .compat import Concatenate, ParamSpec, Unpack
from .exc import AbsolidixAsyncRuntimeWarning
from .models.base import AbsolidixBase
from .namespaces.v0_calculations import AbsolidixCalculationOnProgressT
from .namespaces.v0_collections import AbsolidixCollectionsCreateKwargs

AsyncClientGetter = Callable[[], AbsolidixAPIAsync]
ReturnT_co = TypeVar("ReturnT_co", covariant=True)
ParamT = ParamSpec("ParamT")
TimeoutType = Union[float, Literal[False], None]


class AbsolidixNamespaceSyncBase:
    "Base for synchronous namespaces"

    _client_getter: AsyncClientGetter
    _default_timeout: TimeoutType

    def __init__(
        self, client_getter: AsyncClientGetter, default_timeout: TimeoutType = False
    ):
        self._client_getter = client_getter
        self._default_timeout = default_timeout

    def _get_timeout(self, timeout: TimeoutType) -> Optional[float]:
        "Normalize timeout value"
        if timeout is False:
            return None
        if timeout is not None:
            return timeout
        if not self._default_timeout:
            return None
        return self._default_timeout


def to_sync_with_absolidix_client(
    func: Callable[Concatenate[Any, AbsolidixAPIAsync, ParamT], Awaitable[ReturnT_co]],
) -> Callable[Concatenate[Any, ParamT], ReturnT_co]:
    """
    Wraps async AbsolidixNamespaceSync's method.
    - start AbsolidixAPIAsync client,
    - pass it to the method as first argument after Self,
    - close client
    - wrap all with async_to_sync converter
    """

    @wraps(func)
    async def inner(
        self: AbsolidixNamespaceSyncBase, *args: ParamT.args, **kwargs: ParamT.kwargs
    ) -> ReturnT_co:
        """
        Call method with timeout with self, client and other args.
        """
        timeout = self._get_timeout(cast(TimeoutType, kwargs.get("timeout", None)))  # pyright: ignore [reportPrivateUsage]
        async with self._client_getter() as client:  # pyright: ignore [reportPrivateUsage]
            return await asyncio.wait_for(func(self, client, *args, **kwargs), timeout)

    @wraps(func)
    def outer(
        self: AbsolidixNamespaceSyncBase, *args: ParamT.args, **kwargs: ParamT.kwargs
    ) -> ReturnT_co:
        """
        Execute the async method synchronously in sync and async runtime.
        """
        coro = inner(self, *args, **kwargs)
        try:
            asyncio.get_running_loop()  # Triggers RuntimeError if no running event loop

            warn(
                AbsolidixAsyncRuntimeWarning(
                    "Using a synchronous API in an asynchronous runtime. "
                    "Consider switching to AbsolidixAPIAsync."
                )
            )

            # Create a separate thread so we can block before returning
            with ThreadPoolExecutor(1) as pool:
                return pool.submit(lambda: asyncio.run(coro)).result()
        except RuntimeError:
            return asyncio.run(coro)

    return outer


class AbsolidixCalculationsNamespaceSync(AbsolidixNamespaceSyncBase):
    """Calculations endpoints namespace"""

    @to_sync_with_absolidix_client
    async def supported(self, client: AbsolidixAPIAsync):
        "Get supported calculation engines"
        return await client.calculations.supported()


class AbsolidixV0AuthNamespaceSync(AbsolidixNamespaceSyncBase):
    """Authentication endpoints namespace"""

    @to_sync_with_absolidix_client
    async def login(
        self,
        client: AbsolidixAPIAsync,
        email: str,
        password: str,
        timeout: TimeoutType = None,
    ):
        "Login"
        return await client.v0.auth.login(email, password)

    @to_sync_with_absolidix_client
    async def whoami(self, client: AbsolidixAPIAsync, timeout: TimeoutType = None):
        "Get self info"
        return await client.v0.auth.whoami()


class AbsolidixV0DatasourcesNamespaceSync(AbsolidixNamespaceSyncBase):
    """Datasources endpoints namespace"""

    @to_sync_with_absolidix_client
    async def create(
        self,
        client: AbsolidixAPIAsync,
        content: str,
        fmt: Optional[str] = None,
        name: Optional[str] = None,
        timeout: TimeoutType = None,
    ):
        "Create data source and wait for the result"
        return await client.v0.datasources.create(content, fmt, name)

    @to_sync_with_absolidix_client
    async def delete(
        self, client: AbsolidixAPIAsync, data_id: int, timeout: TimeoutType = None
    ):
        "Delete data source by id and wait for the result"
        return await client.v0.datasources.delete(data_id)

    @to_sync_with_absolidix_client
    async def list(self, client: AbsolidixAPIAsync, timeout: TimeoutType = None):
        "List data sources and wait for the result"
        return await client.v0.datasources.list()

    @to_sync_with_absolidix_client
    async def get(
        self, client: AbsolidixAPIAsync, data_id: int, timeout: TimeoutType = None
    ) -> Optional[AbsolidixDataSourceDTO]:
        "Get data source by id"
        return await client.v0.datasources.get(data_id)

    @to_sync_with_absolidix_client
    async def get_parents(
        self, client: AbsolidixAPIAsync, data_id: int, timeout: TimeoutType = None
    ) -> Sequence[AbsolidixDataSourceDTO]:
        "Get parent data sources by id"
        return await client.v0.datasources.get_parents(data_id)

    @to_sync_with_absolidix_client
    async def get_children(
        self, client: AbsolidixAPIAsync, data_id: int, timeout: TimeoutType = None
    ) -> Sequence[AbsolidixDataSourceDTO]:
        "Get children data sources by id"
        return await client.v0.datasources.get_children(data_id)

    @to_sync_with_absolidix_client
    async def get_content(
        self, client: AbsolidixAPIAsync, data_id: int, timeout: TimeoutType = None
    ):
        "Get data source by id"
        return await client.v0.datasources.get_content(data_id)


class AbsolidixV0CalculationsNamespaceSync(AbsolidixNamespaceSyncBase):
    """Calculations endpoints namespace"""

    @to_sync_with_absolidix_client
    async def cancel(
        self, client: AbsolidixAPIAsync, calc_id: int, timeout: TimeoutType = None
    ):
        "Cancel calculation and wait for the result"
        return await client.v0.calculations.cancel(calc_id)

    @to_sync_with_absolidix_client
    async def create(
        self,
        client: AbsolidixAPIAsync,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,
        timeout: TimeoutType = None,
    ):
        "Create calculation and wait for the result"
        return await client.v0.calculations.create(data_id, engine, input)

    @to_sync_with_absolidix_client
    async def get_results(
        self,
        client: AbsolidixAPIAsync,
        calc_id: int,
        on_progress: Optional[AbsolidixCalculationOnProgressT] = None,
        timeout: TimeoutType = None,
    ):
        "Waits for the end of the calculation and returns the results"
        return await client.v0.calculations.get_results(calc_id, on_progress)

    @to_sync_with_absolidix_client
    async def create_get_results(
        self,
        client: AbsolidixAPIAsync,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,
        on_progress: Optional[AbsolidixCalculationOnProgressT] = None,
        timeout: TimeoutType = None,
    ):
        "Create calculation, wait done and get results"
        return await client.v0.calculations.create_get_results(
            data_id, engine, input, on_progress
        )

    @to_sync_with_absolidix_client
    async def get_engines(self, client: AbsolidixAPIAsync, timeout: TimeoutType = None):
        "Get supported calculation engines"
        return await client.v0.calculations.get_engines()

    @to_sync_with_absolidix_client
    async def list(self, client: AbsolidixAPIAsync, timeout: TimeoutType = None):
        "List all user's calculations and wait for the result"
        return await client.v0.calculations.list()

    @to_sync_with_absolidix_client
    async def get(
        self, client: AbsolidixAPIAsync, calc_id: int, timeout: TimeoutType = None
    ):
        "Get calculation by id"
        return await client.v0.calculations.get(calc_id)


class AbsolidixV0CollectionsNamespaceSync(AbsolidixNamespaceSyncBase):
    """Collections endpoints namespace"""

    @to_sync_with_absolidix_client
    async def create(
        self,
        client: AbsolidixAPIAsync,
        type_id: int,
        title: str,
        timeout: TimeoutType = None,
        **opts: Unpack[AbsolidixCollectionsCreateKwargs],
    ):
        "Create collection and wait for the result"
        return await client.v0.collections.create(type_id, title, **opts)

    @to_sync_with_absolidix_client
    async def list(self, client: AbsolidixAPIAsync, timeout: TimeoutType = None):
        "List user's collections by criteria and wait for the result"
        return await client.v0.collections.list()

    @to_sync_with_absolidix_client
    async def delete(
        self, client: AbsolidixAPIAsync, collection_id: int, timeout: TimeoutType = None
    ):
        "Remove a collection by id and wait for the result"
        return await client.v0.collections.delete(collection_id)


class AbsolidixV0NamespaceSync(AbsolidixNamespaceSyncBase):
    """v0 namespace"""

    def __init__(
        self, client_getter: AsyncClientGetter, default_timeout: Optional[float] = False
    ):
        super().__init__(client_getter, default_timeout)
        self.auth = AbsolidixV0AuthNamespaceSync(client_getter, default_timeout)
        self.calculations = AbsolidixV0CalculationsNamespaceSync(
            client_getter, default_timeout
        )
        self.collections = AbsolidixV0CollectionsNamespaceSync(
            client_getter, default_timeout
        )
        self.datasources = AbsolidixV0DatasourcesNamespaceSync(
            client_getter, default_timeout
        )


class AbsolidixAPI(AbsolidixBase):
    """Absolidix API synchronous client"""

    def __init__(
        self,
        base_url: StrOrURL,
        **opts: Unpack[AbsolidixAPIKwargs],
    ):
        """
        Initialize sync Absolidix client.
        Sync client is a tiny wrapper over full async client.

        **Arguments**:

        `bese_url`
        URL of Absolidix BFF server. `str` or `yarl.URL`.

        `headers` (Optional)
        Optional dictionary of always sent headers. Used if `session` is omitted.

        `timeout` (Optional)
        Optional float timeout in seconds. None if no timeout. False if not set.
        Used as `aiohttp` timeout if `session` is omitted.
        Used as global timeout for SSE responses.

        `client_name` (Optional)
        Optional string for user agent.
        """
        timeout = opts.get("timeout", None)
        self._ns_calculations = AbsolidixCalculationsNamespaceSync(
            partial(AbsolidixAPIAsync, base_url, **opts), timeout
        )
        self._ns_v0 = AbsolidixV0NamespaceSync(
            partial(AbsolidixAPIAsync, base_url, **opts), timeout
        )

    @property
    def calculations(
        self,
    ) -> AbsolidixCalculationsNamespaceSync:
        """Property to access the calculations namespace."""
        return self._ns_calculations

    @property
    def v0(self) -> AbsolidixV0NamespaceSync:
        """Property to access the v0 namespace."""
        return self._ns_v0
