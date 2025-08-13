"""Base of DTOs"""

from datetime import datetime

from ..compat import NotRequired, TypedDict


class AbsolidixTimestampsDTO(TypedDict):
    "Response with timestamps"

    created_at: NotRequired[datetime]
    updated_at: NotRequired[datetime]
