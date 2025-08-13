"Test AbsolidixClient"

import asyncio
import json
import logging
from asyncio import Task
from contextlib import suppress
from itertools import count
from typing import Optional, Union

import freezegun
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPException,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPMisdirectedRequest,
    HTTPNotFound,
    HTTPOk,
    HTTPPaymentRequired,
    HTTPTooManyRequests,
    HTTPUnauthorized,
)
from aiohttp_sse_client.client import MessageEvent
from yarl import URL

from absolidix_client import AbsolidixNoAuth, AbsolidixTokenAuth
from absolidix_client.client import AbsolidixClient
from absolidix_client.exc import (
    AbsolidixAuthenticationException,
    AbsolidixConnectionException,
    AbsolidixError,
    AbsolidixException,
    AbsolidixNotFoundException,
    AbsolidixPayloadException,
    AbsolidixQuotaException,
)
from tests.helpers import TestClient, random_word

freezegun.configure(extend_ignore_list=["aiohttp"])

TOKEN = random_word(10)

PATH_CHECK_TOKEN_AUTH = "/check_bearer"
PATH_CHECK_PARAMS = "/check_params"
PATH_CHECK_HEADER = "/check_header"
PATH_CHECK_DATA = "/check_data"
PATH_TOO_MANY = "/too_many"
TOO_MANY_COUNTER = count(0)
PATH_SLOW_RESPONSE = "/slow"
PATH_PAYLOAD_ERROR = "/payload_error"
PATH_ECHO_STATUS = "/echo_status"
PATH_JSON_CASE_CHECK_STATUS = "/json_case_check"
PATH_SSE_SIMPLE = "/sse"


async def check_token_auth_handler(request: web.Request) -> web.Response:
    "Request handler"
    if request.headers.get("Authorization") == f"Bearer {TOKEN}":
        return web.Response(status=HTTPOk.status_code)
    return web.Response(status=HTTPUnauthorized.status_code)


async def check_params_handler(request: web.Request) -> web.Response:
    "Request handler"
    if request.query.get("param") == "ok":
        return web.Response(status=HTTPOk.status_code)
    return web.Response(status=HTTPBadRequest.status_code)


async def check_query_handler(request: web.Request) -> web.Response:
    "Request handler"
    if request.query.get("param") == "ok":
        return web.Response(status=HTTPOk.status_code)
    return web.Response(status=HTTPBadRequest.status_code)


async def check_header_handler(request: web.Request) -> web.Response:
    "Request handler"
    if request.headers.get("header") == "ok":
        return web.Response(status=HTTPOk.status_code)
    return web.Response(status=HTTPBadRequest.status_code)


async def check_data_handler(request: web.Request) -> web.Response:
    "Request handler"
    if await request.content.read() == b"ok":
        return web.Response(status=HTTPOk.status_code)
    return web.Response(status=HTTPBadRequest.status_code)


async def too_many_handler(_: web.Request) -> web.Response:
    "Request handler"
    if next(TOO_MANY_COUNTER) < 2:
        return web.Response(status=HTTPTooManyRequests.status_code)
    return web.Response(status=HTTPOk.status_code)


async def slow_response_handler(_: web.Request) -> web.Response:
    "Request handler"
    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    return web.Response(status=HTTPOk.status_code)


async def payload_error_handler(_: web.Request) -> web.Response:
    "Request handler"
    resp = web.Response(text="text")
    resp.headers["Content-Encoding"] = "gzip"
    return resp


async def echo_status_handler(request: web.Request) -> web.Response:
    "Request handler"
    status_code = int(request.query.get("status_code", 400))
    content_type = request.query.get("content_type")
    charset = content_type and "utf-8"
    body = request.query.get("body")
    return web.Response(
        status=status_code, content_type=content_type, charset=charset, body=body
    )


async def json_case_check_status_handler(request: web.Request) -> web.Response:
    "Request handler"
    payload = await request.json()
    out_data = {"original": json.dumps(payload), "payload": payload}
    return web.json_response(out_data)


async def sse_simple_handler(request: web.Request) -> web.Response:
    "Request handler"
    status_code = int(request.query.get("force_status", HTTPOk.status_code))
    if request.headers.get("Authorization") != f"Bearer {TOKEN}" or status_code == 401:
        return web.Response(
            status=HTTPUnauthorized.status_code, content_type="text/plain"
        )

    event_type = request.query.get("event_type", "message")
    event_data = request.query.get("event_data", random_word(10))
    body = f"event: {event_type}\ndata: {event_data}\n\n"
    resp = web.Response(status=status_code, body=body)
    resp.content_type = "text/event-stream"
    resp.headers["Cache-Control"] = "no-store"
    return resp


async def create_app() -> web.Application:
    "Create web application"
    app = web.Application()
    app.router.add_get(PATH_CHECK_TOKEN_AUTH, check_token_auth_handler)
    app.router.add_get(PATH_CHECK_PARAMS, check_params_handler)
    app.router.add_get(PATH_CHECK_HEADER, check_header_handler)
    app.router.add_post(PATH_CHECK_DATA, check_data_handler)
    app.router.add_get(PATH_TOO_MANY, too_many_handler)
    app.router.add_get(PATH_SLOW_RESPONSE, slow_response_handler)
    app.router.add_get(PATH_PAYLOAD_ERROR, payload_error_handler)
    app.router.add_get(PATH_ECHO_STATUS, echo_status_handler)
    app.router.add_post(PATH_JSON_CASE_CHECK_STATUS, json_case_check_status_handler)
    app.router.add_get(PATH_SSE_SIMPLE, sse_simple_handler)
    return app


@pytest.fixture
async def cli():
    "Create test client"
    async with TestClient(TestServer(await create_app())) as client:
        yield client


@pytest.fixture
async def client(cli: TestClient) -> AbsolidixClient:
    "Create AbsolidixClient"
    return AbsolidixClient(
        session=cli.session,
        base_url=cli.make_url(""),
        auth=AbsolidixTokenAuth(TOKEN),
    )


async def test_relative_url(cli: TestClient):
    "Test error on relative base url"

    with pytest.raises(TypeError) as exc_info:
        AbsolidixClient(
            session=cli.session, base_url=URL("/relative"), auth=AbsolidixNoAuth()
        )
    assert "URL" in exc_info.value.args[0], (
        "AbsolidixClient should reject relative base url"
    )


async def test_token_auth_forced(
    client: AbsolidixClient,
):
    "Test successful authentication"
    resp = await client.request(URL(PATH_CHECK_TOKEN_AUTH), auth_required=True)
    assert resp.ok, "Client should authenticate"


async def test_params(
    client: AbsolidixClient,
):
    "Test query param passthrough"
    resp = await client.request(URL(PATH_CHECK_PARAMS), params={"param": "ok"})
    assert resp.ok, "Client should pass query param"


async def test_header(
    client: AbsolidixClient,
):
    "Test header passthrough"
    resp = await client.request(URL(PATH_CHECK_HEADER), headers={"header": "ok"})
    assert resp.ok, "Client should pass header"


async def test_data(
    client: AbsolidixClient,
):
    "Test data passthrough"
    resp = await client.request(URL(PATH_CHECK_DATA), data="ok", method="POST")
    assert resp.ok, "Client should pass data"


async def test_relative_target_url(
    client: AbsolidixClient,
):
    "Test relative targer url not started with '/'"
    resp = await client.request(URL(PATH_CHECK_TOKEN_AUTH[1:]))
    assert resp.ok, "Client should not fail"


@freezegun.freeze_time("1970-01-01", auto_tick_seconds=10)
async def test_too_many_request(
    client: AbsolidixClient,
):
    "Test too many requests"
    resp = await client.request(URL(PATH_TOO_MANY))
    assert resp.ok, "Should tolerate too many requests"


async def test_client_connection_error(
    client: AbsolidixClient,
):
    "Test ClientConnectionError"

    with pytest.raises(AbsolidixConnectionException) as exc_info:
        await client.request(URL("http://0.0.0.0:1"))
    assert "Request exception" in exc_info.value.args[0], (
        "AbsolidixClient should handle ClientConnectionError"
    )


async def test_client_payload_error(
    client: AbsolidixClient,
):
    "Test ClientPayloadError"

    with pytest.raises(AbsolidixException) as exc_info:
        await client.request(URL(PATH_PAYLOAD_ERROR))
    assert "Broken" in exc_info.value.args[0], (
        "AbsolidixClient should handle ClientPayloadError"
    )
    query = {
        "status_code": HTTPOk.status_code,
        "content_type": "application/json",
        "body": random_word(10),
    }
    with pytest.raises(AbsolidixException) as exc_info:
        await client.request(URL(PATH_ECHO_STATUS).with_query(query))
    assert "Broken" in exc_info.value.args[0], (
        "AbsolidixClient should handle JSONDecodeError"
    )


async def test_timeout_error(
    client: AbsolidixClient,
):
    "Test timeout"

    with pytest.raises(AbsolidixConnectionException) as exc_info:
        await client.request(URL(PATH_SLOW_RESPONSE), timeout=0.0001)
    assert "Timeout" in exc_info.value.args[0], "AbsolidixClient should handle timeout"


@pytest.mark.parametrize(
    "status,exception",
    [
        (HTTPForbidden, AbsolidixAuthenticationException),
        (HTTPUnauthorized, AbsolidixAuthenticationException),
        (HTTPNotFound, AbsolidixNotFoundException),
        (HTTPPaymentRequired, AbsolidixQuotaException),
        (HTTPMisdirectedRequest, AbsolidixError),
        (HTTPMisdirectedRequest, AbsolidixError),
        (HTTPBadRequest, AbsolidixPayloadException),
    ],
)
async def test_http_status(
    client: AbsolidixClient, status: HTTPException, exception: type[BaseException]
):
    "Test http status codes"

    def get_url(
        status: int, content_type: Optional[str] = None, body: Optional[str] = None
    ):
        query: dict[str, Union[int, str]] = {"status_code": status}
        if content_type:
            query["content_type"] = content_type
        if body:
            query["body"] = body
        return URL(PATH_ECHO_STATUS).with_query(query)

    if status == HTTPBadRequest:
        body = random_word(16)
        url = get_url(status.status_code, "text/plain", body)
        with pytest.raises(exception):
            await client.request(url)
        body = {"error": random_word(16)}
        url = get_url(
            HTTPBadRequest.status_code,
            content_type="application/json",
            body=json.dumps(body),
        )
        with pytest.raises(exception):
            await client.request(url)
    else:
        with pytest.raises(exception):
            await client.request(get_url(status.status_code))


async def test_sse_msg_receive(
    client: AbsolidixClient,
):
    "Test simple SSE event receive"

    task: Optional[Task[None]] = None
    event_type = random_word(8)
    event_data = random_word(16)

    def on_message(evt: MessageEvent):
        assert evt.type == event_type and evt.data == event_data, (
            "Should receive same SSE event as requested"
        )
        if task:
            task.cancel()

    query = {"event_type": event_type, "event_data": event_data}
    task = asyncio.create_task(
        client.sse(URL(PATH_SSE_SIMPLE).with_query(query), on_message)
    )
    await asyncio.wait_for(task, 1)


async def test_sse_timeout(
    client: AbsolidixClient,
    caplog: pytest.LogCaptureFixture,
):
    "Test reconnect on timeout"
    task: Optional[Task[None]] = None

    def on_message(_: MessageEvent):
        pass

    def timeouted_in_log() -> bool:
        recs = list(filter(lambda x: "timeouted" in x.message, caplog.records))
        return len(recs) >= 1

    async def wait_timeouted_in_log():
        while not timeouted_in_log():
            await asyncio.sleep(0.001)

    with caplog.at_level(logging.WARNING):
        task = asyncio.create_task(
            client.sse(URL(PATH_SSE_SIMPLE), on_message, timeout=0.00000001)
        )
        await asyncio.wait_for(wait_timeouted_in_log(), 1)
        task.cancel()
        await task

    assert timeouted_in_log(), "Client should log about timeout"


async def test_sse_connection_error(
    client: AbsolidixClient,
):
    "Test sse connection error"

    def on_message(_: MessageEvent):
        pass

    with pytest.raises(AbsolidixConnectionException) as exc_info:
        await asyncio.create_task(client.sse(URL("http://0.0.0.0:1"), on_message))
    assert "Connection error" in exc_info.value.args[0], (
        "Client should throw exception on connection errors"
    )


async def test_sse_response_errors(
    client: AbsolidixClient,
):
    "Test sse connection error"

    task: Optional[Task[None]] = None

    def on_message(_: MessageEvent):
        pass

    query = {"force_status": HTTPTooManyRequests.status_code}
    task = asyncio.create_task(
        client.sse(URL(PATH_SSE_SIMPLE).with_query(query), on_message)
    )
    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(task, 0.01)

    query = {"force_status": HTTPInternalServerError.status_code}
    task = asyncio.create_task(
        client.sse(URL(PATH_SSE_SIMPLE).with_query(query), on_message)
    )
    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(task, 0.01)

    query = {"force_status": HTTPNotFound.status_code}
    with pytest.raises(AbsolidixNotFoundException):
        await asyncio.create_task(
            client.sse(URL(PATH_SSE_SIMPLE).with_query(query), on_message)
        )
