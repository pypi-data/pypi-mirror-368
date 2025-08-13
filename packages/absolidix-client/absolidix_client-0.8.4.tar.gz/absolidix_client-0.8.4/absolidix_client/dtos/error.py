"""Error DTOs"""

from typing import Union

from ..compat import TypedDict


class AbsolidixErrorMessageDTO(TypedDict):
    "Error's raw transport error payload DTO"

    message: str


class AbsolidixErrorDTO(TypedDict):
    "Error DTO"

    status: int
    error: Union[AbsolidixErrorMessageDTO, str]
