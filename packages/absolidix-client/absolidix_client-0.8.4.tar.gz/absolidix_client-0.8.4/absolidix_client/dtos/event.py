"""SSE DTOs"""

from typing import Literal, Union
from collections.abc import Sequence
from ..compat import TypedDict
from .calculation import AbsolidixCalculationDTO
from .collection import AbsolidixCollectionDTO, AbsolidixCollectionTypeDTO
from .datasource import AbsolidixDataSourceDTO
from .error import AbsolidixErrorDTO

AbsolidixEventType = Literal[
    "calculations", "collections", "datasources", "errors", "pong"
]


class AbsolidixErrorEventDataDTO(TypedDict):
    "Errors event data DTO"

    req_id: str
    data: Sequence[AbsolidixErrorDTO]


class AbsolidixErrorEventDTO(TypedDict):
    "Errors event DTO"

    type: Literal["errors"]
    data: AbsolidixErrorEventDataDTO


class AbsolidixPongEventDTO(TypedDict):
    "Pong event DTO"

    type: Literal["ping"]
    data: Literal["pong"]


class AbsolidixDataSourcesEventDataDTO(TypedDict):
    "Data sources event data DTO"

    req_id: str
    data: Sequence[AbsolidixDataSourceDTO]
    total: int
    types: Sequence[AbsolidixCollectionTypeDTO]


class AbsolidixDataSourcesEventDTO(TypedDict):
    "Data sources event DTO"

    type: Literal["datasources"]
    data: AbsolidixDataSourcesEventDataDTO


class AbsolidixCalculationsEventDataDTO(TypedDict):
    "Calculations event data DTO"

    req_id: str
    data: Sequence[AbsolidixCalculationDTO]
    total: int
    types: Sequence[AbsolidixCollectionTypeDTO]


class AbsolidixCalculationsEventDTO(TypedDict):
    "Calculations event DTO"

    type: Literal["calculations"]
    data: AbsolidixCalculationsEventDataDTO


class AbsolidixCollectionsEventDataDTO(TypedDict):
    "Collections event data DTO"

    req_id: str
    data: Sequence[AbsolidixCollectionDTO]
    total: int
    types: Sequence[AbsolidixCollectionTypeDTO]


class AbsolidixCollectionsEventDTO(TypedDict):
    "Collections event DTO"

    type: Literal["collections"]
    data: AbsolidixCollectionsEventDataDTO


AbsolidixEventDTO = Union[
    AbsolidixCalculationsEventDTO,
    AbsolidixCollectionsEventDTO,
    AbsolidixDataSourcesEventDTO,
    AbsolidixErrorEventDTO,
    AbsolidixPongEventDTO,
]
