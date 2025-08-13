"""Small helpers"""

import json
import re
from collections.abc import Awaitable
from contextlib import suppress
from copy import deepcopy
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPMisdirectedRequest,
    HTTPNotFound,
    HTTPPaymentRequired,
    HTTPUnauthorized,
)

from .compat import ParamSpec, TypeAlias, TypeGuard
from .dtos import (
    AbsolidixErrorDTO,
    AbsolidixErrorEventDataDTO,
    AbsolidixErrorEventDTO,
    AbsolidixErrorMessageDTO,
)
from .exc import (
    AbsolidixAuthenticationException,
    AbsolidixError,
    AbsolidixNotFoundException,
    AbsolidixPayloadException,
    AbsolidixQuotaException,
)

JSONT: TypeAlias = Union[dict[str, "JSONT"], list["JSONT"], str, int, float, bool, None]

LAST_Z_REGEX = re.compile(r"Z$", re.IGNORECASE)

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def parse_rfc3339(dt_str: Any) -> Optional[datetime]:
    "Parse RFC 3339 date string to datetime object"
    if isinstance(dt_str, datetime):
        return dt_str

    if not dt_str:
        return None

    if dt_str.endswith("Z"):
        dt_str = LAST_Z_REGEX.sub("+00:00", dt_str)

    with suppress(ValueError):
        return datetime.fromisoformat(dt_str)

    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        with suppress(ValueError):
            return datetime.strptime(dt_str, fmt)


_DT = TypeVar("_DT", bound=dict[str, Any])


def convert_dict_values_to_dt(data: _DT) -> _DT:
    "Converts dictionary values to datetime"

    converted = deepcopy(data)
    for key, val in data.items():
        if isinstance(val, str):
            converted[key] = parse_rfc3339(val) or val
        elif isinstance(val, dict):
            converted[key] = convert_dict_values_to_dt(val)  # pyright: ignore[reportUnknownArgumentType]
        elif isinstance(val, list):
            converted[key] = [
                convert_dict_values_to_dt(x) if isinstance(x, dict) else x  # pyright: ignore[reportUnknownArgumentType]
                for x in val  # pyright: ignore[reportUnknownVariableType]
            ]
        elif isinstance(val, tuple):
            converted[key] = tuple(
                convert_dict_values_to_dt(x) if isinstance(x, dict) else x  # pyright: ignore[reportUnknownArgumentType]
                for x in val  # pyright: ignore[reportUnknownVariableType]
            )

    return converted


def convert_dict_values_from_dt(data: _DT) -> _DT:
    "Converts dictionary values from datetime to string"

    converted = deepcopy(data)
    for key, val in data.items():
        if isinstance(val, datetime):
            converted[key] = val.isoformat()
        elif isinstance(val, dict):
            converted[key] = convert_dict_values_from_dt(val)  # pyright: ignore[reportUnknownArgumentType]
        elif isinstance(val, list):
            converted[key] = [
                convert_dict_values_from_dt(x) if isinstance(x, dict) else x  # pyright: ignore[reportUnknownArgumentType]
                for x in val  # pyright: ignore[reportUnknownVariableType]
            ]
        elif isinstance(val, tuple):
            converted[key] = tuple(
                convert_dict_values_from_dt(x) if isinstance(x, dict) else x  # pyright: ignore[reportUnknownArgumentType]
                for x in val  # pyright: ignore[reportUnknownVariableType]
            )

    return converted


def absolidix_json_decoder(
    json_str: str, *args: tuple[Any, ...], **kwargs: dict[str, Any]
):
    "Json decoder but with conversion to snake case and datetime"
    payload: JSONT = json.loads(json_str, *args, **kwargs)
    if isinstance(payload, dict):
        return convert_dict_values_to_dt(payload)
    return payload


def absolidix_json_encoder(
    obj: JSONT, *args: tuple[Any, ...], **kwargs: dict[str, Any]
):
    "Json encoder but with conversion to camel case"
    payload = obj
    if isinstance(obj, dict):
        payload = convert_dict_values_from_dt(obj)
    return json.dumps(payload, *args, **kwargs)


def is_absolidix_error_error_dto(something: Any) -> TypeGuard[AbsolidixErrorMessageDTO]:
    "AbsolidixErrorMessageDTO type guard"
    return (
        isinstance(something, dict)
        and "message" in something
        and isinstance(something["message"], str)
    )


def is_absolidix_error_dto(something: Any) -> TypeGuard[AbsolidixErrorDTO]:
    "AbsolidixErrorDTO type guard"
    return (
        isinstance(something, dict)
        and "status" in something
        and "error" in something
        and (
            isinstance(something["error"], str)
            or is_absolidix_error_error_dto(something["error"])
        )
    )


def is_absolidix_error_event_data_dto(
    something: Any,
) -> TypeGuard[AbsolidixErrorEventDataDTO]:
    "AbsolidixErrorEventDataDTO type guard"
    return (
        isinstance(something, dict)
        and "req_id" in something
        and "data" in something
        and isinstance(something["data"], list)
        and all(is_absolidix_error_dto(x) for x in something["data"])  # pyright: ignore[reportUnknownVariableType]
    )


def is_absolidix_errors_evt_dto(something: Any) -> TypeGuard[AbsolidixErrorEventDTO]:
    "AbsolidixEventDTO type guard"
    return (
        isinstance(something, dict)
        and "type" in something
        and isinstance(something["type"], str)
        and something["type"] == "errors"
        and "data" in something
        and is_absolidix_error_event_data_dto(something["data"])
    )


def http_to_absolidix_error_map(status: int) -> type[AbsolidixError]:
    "Map HTTP exception to AbsolidixError"
    err = AbsolidixError
    if status in (HTTPForbidden.status_code, HTTPUnauthorized.status_code):
        err = AbsolidixAuthenticationException
    if status == HTTPNotFound.status_code:
        err = AbsolidixNotFoundException
    if status == HTTPBadRequest.status_code:
        err = AbsolidixPayloadException
    if status == HTTPPaymentRequired.status_code:
        err = AbsolidixQuotaException
    if status == HTTPMisdirectedRequest.status_code:
        err = AbsolidixError
    return err


def absolidix_error_to_raise(dto: AbsolidixErrorDTO):
    "Raise AbsolidixErrorDTO"
    if isinstance(dto["error"], str):
        msg = dto["error"]
    else:
        msg = dto["error"]["message"]
    err = http_to_absolidix_error_map(dto.get("status"))
    raise err(status=dto["status"], message=msg)


def raise_on_absolidix_error(
    func: Callable[Param, Awaitable[RetType]],
) -> Callable[Param, Awaitable[RetType]]:
    """
    Method wrapper. If there is an AbsolidixErrorDTO in result, than raise AbsolidixError.
    """

    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any):
        result = await func(*args, **kwargs)
        if is_absolidix_error_dto(result):
            absolidix_error_to_raise(result)

        return result

    return wrapped


def raise_on_absolidix_error_in_event(
    func: Callable[Param, Awaitable[RetType]],
) -> Callable[Param, Awaitable[RetType]]:
    "Raise on AbsolidixErrorDTO in AbsolidixEventDTO"

    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any):
        result = await func(*args, **kwargs)
        if is_absolidix_errors_evt_dto(result):
            errors = result.get("data", {}).get("data", [])
            if errors:
                absolidix_error_to_raise(errors[-1])

        return result

    return wrapped
