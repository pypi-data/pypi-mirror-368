"""Data sources DTOs"""

from collections.abc import Sequence
from enum import Enum

from ..compat import TypedDict
from .base import AbsolidixTimestampsDTO
from .collection import AbsolidixCollectionDTO


class DataSourceType(int, Enum):
    """The basic data types supported"""

    STRUCTURE = 1
    CALCULATION = 2
    PROPERTY = 3
    WORKFLOW = 4
    PATTERN = 5
    USER_INPUT = 6


class AbsolidixDataSourceDTO(AbsolidixTimestampsDTO):
    """A basic data item definition"""

    id: int
    parents: Sequence[int]
    children: Sequence[int]
    user_id: int
    user_first_name: str
    user_last_name: str
    user_email: str
    name: str
    content: str
    type: int
    collections: Sequence[AbsolidixCollectionDTO]


class AbsolidixDataSourceContentOnlyDTO(TypedDict):
    """Helper definition"""

    content: str
