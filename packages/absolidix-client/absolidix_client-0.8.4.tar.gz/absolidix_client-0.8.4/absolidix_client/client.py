"""Low level http and SSE client"""

import json
from asyncio import CancelledError, sleep
from asyncio import TimeoutError as AsyncioTimeoutError
from collections.abc import Awaitable, Callable
from concurrent.futures import TimeoutError as FuturesTimeoutError
from datetime import timedelta
from typing import Any, Optional, Union

import aiohttp
from aiohttp import ClientResponse, ClientTimeout, RequestInfo
from aiohttp.client import (
    _RequestContextManager,  # pyright: ignore [reportPrivateUsage]
)
from aiohttp.client_exceptions import (
    ClientConnectionError,
    ClientPayloadError,
    ClientResponseError,
)
from aiohttp.typedefs import LooseHeaders
from aiohttp.web_exceptions import (
    HTTPInternalServerError,
    HTTPTooManyRequests,
    HTTPUnauthorized,
)
from aiohttp_sse_client import client as sse_client
from yarl import URL, Query

from .compat import TypedDict, Unpack
from .const import HttpMethods
from .exc import AbsolidixConnectionException, AbsolidixException
from .helpers import (
    JSONT,
    absolidix_json_decoder,
    absolidix_json_encoder,
    http_to_absolidix_error_map,
)
from .models import AbsolidixBase, AbsolidixNoAuth, BaseAuthenticator


class AiohttpSessionRequestOptionsBase(TypedDict, total=False):
    params: Query
    json: Any
    data: Any
    headers: Union[LooseHeaders, None]


class AiohttpSessionRequestOptions(AiohttpSessionRequestOptionsBase, total=False):
    "Partial implementation of the private aiohttp.client._RequestOptions"

    timeout: "Union[ClientTimeout, None]"
    raise_for_status: Union[None, bool, Callable[[ClientResponse], Awaitable[None]]]


class ClientRequestKwargs(AiohttpSessionRequestOptionsBase, total=False):
    "AbsolidixClient.create kwargs"

    method: HttpMethods
    timeout: float
    auth_required: bool


class AbsolidixClient(AbsolidixBase):
    """
    Client to handle API calls.
    Don't use this directly, use `absolidix_client.absolidix.Absolidix` instead to get the client.
    """

    _auth: BaseAuthenticator
    _base_url: URL

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: URL,
        auth: Optional[BaseAuthenticator] = None,
    ) -> None:
        """
        Initialize the Absolidix API client.
        **Arguments:**
        `session`: The aiohttp client session to use for making requests.
        `base_url`: Root URL in form of `yarl.URL`.
        `auth`: Authenticator, subclass of `BaseAuthenticator`.
        """
        self._session = session
        if self._session.json_serialize is not absolidix_json_encoder:
            self._session._json_serialize = absolidix_json_encoder  # pyright: ignore[reportPrivateUsage]
        self._auth = auth or AbsolidixNoAuth()
        if not base_url.is_absolute():
            raise TypeError("Base URL should be absolute")
        self._base_url = base_url

    def _url_rel_to_abs(self, url: URL) -> URL:
        "If url is relative, join it with base url, else return as is"
        if url.is_absolute():
            return url
        if url.path.startswith("/"):
            return self._base_url.join(url)
        return (self._base_url / url.path).with_query(url.query)

    async def _do_auth(self, force: bool = False) -> None:
        async with self._auth.lock:
            if force or await self._auth.should_update(self._session, self._base_url):
                await self._auth.authenticate(self._session, self._base_url)

    @staticmethod
    def _raise_for_status(
        status: int, req_info: RequestInfo, msg: Optional[str] = None
    ) -> None:
        if status < 400:
            return
        msg = f"Response exception for {req_info.url!s} with code {status}: {msg!s}"
        proto_err = http_to_absolidix_error_map(status)
        raise proto_err(status=status, message=msg) from ClientResponseError(
            req_info, message=msg, status=status, history=()
        )

    async def _request(
        self, url: URL, **opts: Unpack[ClientRequestKwargs]
    ) -> ClientResponse:
        """
        Makes an HTTP request to the specified endpoint using the specified parameters.
        """
        url = self._url_rel_to_abs(url)
        method = opts.get("method", "GET")
        auth_required = opts.get("auth_required", False)
        aio_opts: AiohttpSessionRequestOptions = {}
        if "params" in opts:
            aio_opts["params"] = opts["params"]
        if "timeout" in opts:
            aio_opts["timeout"] = ClientTimeout(opts["timeout"])
        if "headers" in opts:
            aio_opts["headers"] = opts["headers"]
        if "json" in opts:
            aio_opts["json"] = opts["json"]
        if "data" in opts:
            aio_opts["data"] = opts["data"]
        aio_opts["raise_for_status"] = False

        # preauthenticate
        if auth_required:
            await self._do_auth()

        try:
            result = await self._session.request(method, url, **aio_opts)

            # redo if failed because of auth
            if result.status == HTTPUnauthorized.status_code:
                # forced auth for first request
                # normal auth (only if needed) for all other
                await self._do_auth(force=not self._auth.lock.locked())
                result.close()
                result = await self._session.request(method, url, **aio_opts)
            # rate limit - redo all
            if result.status == HTTPTooManyRequests.status_code:
                await sleep(10)
                result.close()
                return await self._request(url, **opts)

        except ClientConnectionError as exc:
            raise AbsolidixConnectionException(
                f"Request exception for {str(url)!r} with - {exc}"
            ) from exc

        except (TimeoutError, AsyncioTimeoutError, FuturesTimeoutError):
            raise AbsolidixConnectionException(
                f"Timeout of {opts.get('timeout')} reached while waiting for {str(url)}"
            ) from None

        except BaseException as exc:  # pragma: no cover  # noqa: B036
            raise AbsolidixException(
                f"Unexpected exception for {str(url)!r} with - {exc}"
            ) from exc

        msg = None
        try:
            body = None
            if result.content_type.startswith("application/json"):
                body: JSONT = await result.json(
                    encoding="utf-8",
                    content_type=result.content_type,
                    loads=absolidix_json_decoder,
                )
                if (
                    isinstance(body, dict)
                    and "error" in body
                    and body["error"] is not None
                ):
                    msg = str(body["error"])
            elif result.content_type.startswith("text/"):
                msg = await result.text("utf-8")
            else:
                msg = str(await result.read())
        except (ClientPayloadError, json.JSONDecodeError) as exc:
            raise AbsolidixException(
                f"Broken payload data from {str(url)!r}: {exc}"
            ) from exc
        except BaseException as exc:  # pragma: no cover  # noqa: B036
            raise AbsolidixException(
                f"Could not handle response data from {str(url)!r} with - {exc}"
            ) from exc

        self._raise_for_status(result.status, result.request_info, msg)

        return result

    def request(
        self,
        url: URL,
        **opts: Unpack[ClientRequestKwargs],
    ):
        """
        Makes an HTTP request to the specified endpoint using the specified parameters.
        This method is asynchronous, meaning that it will not block the execution
        of the program while the request is being made and processed.
        **Arguments**:
        -  `url` (Required): The API endpoint to call.
        **Optional arguments**:
        - `data`: The data to include in the request body. Can be a dictionary,
           a string, or None.
        - `headers`: The headers to include in the request. Can be a dictionary or None.
        - `method`: The HTTP method to use for the request. Defaults to GET.
        - `params`: The query parameters to include in the request.
           Can be a dictionary or None.
        - `timeout`: The maximum amount of time to wait for the request to complete,
          in seconds. Can be an integer or None.
        - `auth_required`: Flag that auth requered for this request
        Returns:
        A `aiohttp.client._RequestContextManager` object representing the API response
        """
        return _RequestContextManager(self._request(url, **opts))

    async def sse(
        self,
        url: URL,
        on_message: Callable[[sse_client.MessageEvent], None],
        on_open: Optional[Callable[[], None]] = None,
        params: Optional[Query] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Creates `aiohttp_sse_client.client.EventSource` object with sensible defaults.
        **Arguments**:
        - `url` (Required): The API endpoint to connect.
        - `on_message`: Message callback
        **Optional arguments**:
        - `on_open`: Callback when connected
        - `params`: The query parameters to include in the request.
           Can be a dictionary or None.
        - `timeout`: Stream timeout, None for infinity
        Returns: None
        """
        url = self._url_rel_to_abs(url)
        original_backoff = 0.1
        backoff = original_backoff

        es_timeout = ClientTimeout(total=timeout, sock_connect=600, sock_read=None)
        while True:
            try:
                if backoff > original_backoff:
                    await sleep(backoff)
                await self._do_auth()
                async with sse_client.EventSource(
                    str(url),
                    reconnection_time=timedelta(seconds=original_backoff),
                    max_connect_retry=0,
                    on_open=on_open,
                    session=self._session,
                    params=params,
                    timeout=es_timeout,
                    read_bufsize=2**19,
                    raise_for_status=True,
                ) as evt_src:
                    backoff = original_backoff
                    async for evt in evt_src:
                        on_message(evt)

            except (TimeoutError, AsyncioTimeoutError, FuturesTimeoutError):
                backoff *= 1.5
                self.logger.warning(
                    "%s endpoint timeouted - reconnecting", self._base_url
                )
                continue

            except CancelledError:
                # task is cancelled - abort
                break

            except (ClientConnectionError, ConnectionError) as exc:
                raise AbsolidixConnectionException(
                    f"Connection error for {str(url)!r} with - {exc}"
                ) from exc

            except ClientResponseError as err:
                if err.status and (
                    err.status == HTTPTooManyRequests.status_code
                    or err.status >= HTTPInternalServerError.status_code
                ):
                    backoff *= 2
                    self.logger.warning(
                        "%s connection error %s - reconnecting in %s seconds",
                        url,
                        err,
                        backoff,
                    )
                    continue
                self._raise_for_status(err.status, err.request_info, err.message)
