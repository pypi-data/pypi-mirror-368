"Test AbsolidixAPIAsync"

import pytest

from absolidix_client import AbsolidixAPIAsync, AbsolidixNoAuth


async def test_relative_url():
    "Test relative url"
    with pytest.raises(TypeError):
        AbsolidixAPIAsync("/relative", auth=AbsolidixNoAuth())
