"Base response DTO"

from ..compat import TypedDict


class AbsolidixRequestIdDTO(TypedDict):
    "Response with request id dictionary"

    req_id: str
