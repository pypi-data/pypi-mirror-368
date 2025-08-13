"Test method wrappers"

from collections.abc import Awaitable
from contextlib import nullcontext
from typing import Any, Callable, TypeVar

import pytest

from absolidix_client.exc import AbsolidixError
from absolidix_client.helpers import (
    raise_on_absolidix_error,
    raise_on_absolidix_error_in_event,
)
from tests.test_helpers_type_guards import (
    IS_ABSOLIDIX_ERROR_DTO_PAMAMS,
    IS_ABSOLIDIX_ERRORS_EVT_DTO_PARAMS,
)

T = TypeVar("T")


def mk_async_fun(x: T) -> Callable[[], Awaitable[T]]:
    "Async echo"

    async def run():
        return x

    return run


@pytest.mark.parametrize("x,expected", IS_ABSOLIDIX_ERROR_DTO_PAMAMS)
async def test_helpers_wrapper_raise_on_absolidix_error(x: Any, expected: bool):
    "Test raise_on_absolidix_error"

    raises = pytest.raises(AbsolidixError) if expected else nullcontext()

    with raises:
        await raise_on_absolidix_error(mk_async_fun(x))()


@pytest.mark.parametrize("x,expected", IS_ABSOLIDIX_ERRORS_EVT_DTO_PARAMS)
async def test_helpers_wrapper_raise_on_absolidix_error_in_event(
    x: Any, expected: bool
):
    "Test raise_on_absolidix_error_in_event"

    raises = pytest.raises(AbsolidixError) if expected else nullcontext()

    with raises:
        await raise_on_absolidix_error_in_event(mk_async_fun(x))()
