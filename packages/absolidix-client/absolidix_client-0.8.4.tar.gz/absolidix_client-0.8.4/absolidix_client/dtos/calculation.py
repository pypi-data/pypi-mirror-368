"""Calculation DTOs"""

from collections.abc import Sequence

from ..compat import NotRequired
from .base import AbsolidixTimestampsDTO
from .datasource import AbsolidixDataSourceDTO


class AbsolidixCalculationDTO(AbsolidixTimestampsDTO):
    "Calculation DTO"

    id: int
    name: str
    user_id: int
    progress: int
    parent: int
    result: NotRequired[Sequence[AbsolidixDataSourceDTO]]
