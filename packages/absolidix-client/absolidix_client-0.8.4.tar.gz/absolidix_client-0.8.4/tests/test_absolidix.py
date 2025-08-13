"Test AbsolidixAPI"

from typing import Union

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from yarl import URL

from absolidix_client import AbsolidixAPI, AbsolidixNoAuth
from absolidix_client.exc import (
    AbsolidixAsyncRuntimeWarning,
    AbsolidixConnectionException,
    AbsolidixException,
)
from tests.helpers import TestClient


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    return app


@pytest.fixture
async def aiohttp_client():
    "Create test client"
    app = await create_app()
    async with TestClient(TestServer(app)) as client:
        yield client


@pytest.fixture
async def base_url(aiohttp_client: TestClient) -> URL:
    "Return base url"
    return aiohttp_client.make_url("")


@pytest.mark.parametrize(
    "default_timeout, timeout, result",
    [
        (False, False, None),
        (False, None, None),
        (False, 1, 1),
        (None, False, None),
        (None, None, None),
        (None, 1, 1),
        (1, False, None),
        (1, None, 1),
        (1, 1, 1),
    ],
)
async def test_sync_ns_timeout(
    base_url: URL,
    default_timeout: Union[bool, None, int],
    timeout: Union[bool, None, int],
    result: Union[bool, None, int],
):
    "Test timeout guessing method"
    client = AbsolidixAPI(base_url, auth=AbsolidixNoAuth(), timeout=default_timeout)

    assert client.v0._get_timeout(timeout) == result  # pyright: ignore[reportPrivateUsage]


async def test_sync_in_async_runtime(base_url: URL):
    """
    Use sync API in an async runtime.
    It's impossible to connect to the test fake server
    because of runtime block by synchronous function call.
    So, we check that:
     - RuntimeError is absent (asyncio.run() cannot be called from a running event loop)
     - AbsolidixAsyncRuntimeWarning is present about misuse of API
     - timeout exception is present
    """
    client = AbsolidixAPI(base_url, auth=AbsolidixNoAuth(), timeout=0.0001)
    with pytest.warns(AbsolidixAsyncRuntimeWarning):
        with pytest.raises((AbsolidixConnectionException, AbsolidixException)):  # noqa: B908
            client.v0.auth.whoami()
