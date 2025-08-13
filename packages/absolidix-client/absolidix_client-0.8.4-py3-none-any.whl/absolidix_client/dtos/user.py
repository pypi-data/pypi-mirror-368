"""User DTOs"""

from ..compat import NotRequired
from .base import AbsolidixTimestampsDTO


class AbsolidixUserDTO(AbsolidixTimestampsDTO):
    "User DTO"

    id: int
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    email: NotRequired[str]
    email_verified: NotRequired[bool]
    role_label: NotRequired[str]
    role_slug: NotRequired[str]
    permissions: NotRequired[dict[str, str]]
    provider: NotRequired[str]
