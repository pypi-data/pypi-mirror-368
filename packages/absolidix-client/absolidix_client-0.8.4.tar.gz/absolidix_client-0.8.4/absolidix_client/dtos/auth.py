"""Authentication DTOs"""

from ..compat import TypedDict


class AbsolidixAuthCredentialsRequestDTO(TypedDict):
    "Authentication request payload"

    email: str
    password: str
