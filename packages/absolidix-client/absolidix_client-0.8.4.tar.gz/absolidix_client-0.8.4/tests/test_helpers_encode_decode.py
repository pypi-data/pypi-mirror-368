"Test helper encoders and decoders"

import json
from datetime import datetime
from typing import Any

import pytest

from absolidix_client.helpers import (
    absolidix_json_decoder,
    absolidix_json_encoder,
    convert_dict_values_from_dt,
    convert_dict_values_to_dt,
    parse_rfc3339,
)

dt_testdata = [
    ({"some": 123}, {"some": 123}),
    (
        {"date": "2001-02-03T04:05:06", "str": "str", "int": int},
        {"date": parse_rfc3339("2001-02-03 04:05:06"), "str": "str", "int": int},
    ),
    (
        {"date": "2001-02-03T04:05:06", "other_date": "2001-02-03T04:05:06+00:00"},
        {
            "date": parse_rfc3339("2001-02-03 04:05:06"),
            "other_date": parse_rfc3339("2001-02-03T04:05:06+00:00"),
        },
    ),
    (
        {"date": "2024-02-02T16:54:11.788905"},
        {"date": parse_rfc3339("2024-02-02T16:54:11.788905")},
    ),
    ({"date": ""}, {"date": ""}),
    ({"date": None}, {"date": None}),
    (
        {"children": [{"date": "2001-02-03T04:05:06"}]},
        {"children": [{"date": parse_rfc3339("2001-02-03 04:05:06")}]},
    ),
    (
        {"children": ({"date": "2001-02-03T04:05:06"},)},
        {"children": ({"date": parse_rfc3339("2001-02-03 04:05:06")},)},
    ),
]

dt_testdata_to_dt = [
    *dt_testdata,
    ({"date": "2001-02-03 04:05:06"}, {"date": parse_rfc3339("2001-02-03 04:05:06")}),
    ({"date": "2001-02-03T04:05:06Z"}, {"date": parse_rfc3339("2001-02-03 04:05:06Z")}),
]


@pytest.mark.parametrize("x,expected", dt_testdata_to_dt)
def test_convert_to_dt(x: dict[str, Any], expected: dict[str, Any]):
    "Test convert_dict_values_to_dt()"
    y = convert_dict_values_to_dt(x)
    assert y == expected, "Converted should match expected value"


@pytest.mark.parametrize("expected,x", dt_testdata)
def test_convert_from_dt(x: dict[str, Any], expected: dict[str, Any]):
    "Test convert_dict_values_to_dt()"
    y = convert_dict_values_from_dt(x)
    assert y == expected, "Converted should match expected value"


dt_now = datetime.now()
json_testdata = [
    ({"test_id": 1}, json.dumps({"test_id": 1})),
    ({"date_time": dt_now}, json.dumps({"date_time": dt_now.isoformat()})),
    ({"nested_dict": {"test_id": 1}}, json.dumps({"nested_dict": {"test_id": 1}})),
    ({"nested_list": [{"test_id": 1}]}, json.dumps({"nested_list": [{"test_id": 1}]})),
]


@pytest.mark.parametrize("x,expected", json_testdata)
def test_json_encoder(x: dict[str, Any], expected: dict[str, Any]):
    "Test absolidix_json_encoder()"
    y = absolidix_json_encoder(x)
    assert y == expected, "Converted should match expected value"


@pytest.mark.parametrize("expected,x", json_testdata)
def test_json_decoder(x: str, expected: dict[str, Any]):
    "Test absolidix_json_decoder()"
    y = absolidix_json_decoder(x)
    assert y == expected, "Converted should match expected value"
