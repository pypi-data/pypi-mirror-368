"""Collections DTOs"""

from collections.abc import Sequence
from typing import Literal, Union

from ..compat import NotRequired, TypedDict
from .base import AbsolidixTimestampsDTO

AbsolidixCollectionVisibility = Union[
    Literal["private"], Literal["shared"], Literal["community"]
]


class AbsolidixCollectionTypeDTO(AbsolidixTimestampsDTO):
    "Collection type DTO"

    id: int
    slug: str
    label: str
    flavor: str


class AbsolidixCollectionCommonDTO(TypedDict):
    "Common fields of collection DTOs"

    title: str
    type_id: int
    datasources: NotRequired[Sequence[int]]
    users: NotRequired[Sequence[int]]


class AbsolidixCollectionCreateDTO(AbsolidixCollectionCommonDTO):
    "Collection create DTO"

    id: NotRequired[int]
    description: NotRequired[str]
    visibility: NotRequired[AbsolidixCollectionVisibility]


class AbsolidixCollectionDTO(AbsolidixCollectionCommonDTO, AbsolidixTimestampsDTO):
    "Collection DTO"

    id: int
    description: str
    visibility: AbsolidixCollectionVisibility

    user_id: int
    user_first_name: NotRequired[str]
    user_last_name: NotRequired[str]
    type_slug: NotRequired[str]
    type_label: NotRequired[str]
    type_flavor: NotRequired[str]
