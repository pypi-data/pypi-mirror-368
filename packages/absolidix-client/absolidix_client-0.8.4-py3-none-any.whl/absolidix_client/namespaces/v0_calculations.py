"""Calculations endpoints namespace"""

from collections.abc import Awaitable, Sequence
from datetime import datetime
from functools import partial
from inspect import iscoroutinefunction
from typing import Callable, Optional, Union, cast
from warnings import warn

from ..dtos import (
    AbsolidixCalculationDTO,
    AbsolidixDataSourceDTO,
    AbsolidixRequestIdDTO,
    DataSourceType,
)
from ..exc import AbsolidixPayloadException
from ..helpers import absolidix_json_decoder, raise_on_absolidix_error
from ..models import act_and_get_result_from_stream
from .base import BaseNamespace

DATA_SOURCE_CALC_RESULT_TYPES = [DataSourceType.PROPERTY, DataSourceType.PATTERN]

AbsolidixCalculationOnProgressT = Callable[
    [AbsolidixCalculationDTO], Union[Optional[bool], Awaitable[Optional[bool]]]
]


class AbsolidixV0CalculationsNamespace(BaseNamespace):
    """Calculations endpoints namespace"""

    async def cancel_event(self, calc_id: int) -> AbsolidixRequestIdDTO:
        "Cancel calculation"
        async with await self._client.request(
            method="DELETE",
            url=self._base_url / str(calc_id),
            auth_required=True,
        ) as resp:
            return await resp.json(loads=absolidix_json_decoder)

    async def cancel(self, calc_id: int) -> None:
        "Cancel calculation and wait for result"
        await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.cancel_event, calc_id)
        )

    async def create_event(
        self,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,
    ) -> AbsolidixRequestIdDTO:
        "Create calculation"
        async with await self._client.request(
            method="POST",
            url=self._base_url,
            json={"dataId": data_id, "engine": engine, "input": input},
            auth_required=True,
        ) as resp:
            return await resp.json(loads=absolidix_json_decoder)

    async def create(
        self,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,
    ) -> Optional[AbsolidixCalculationDTO]:
        "Create calculation and wait for result"
        valid_engines = await self._root.calculations.supported()
        if engine not in valid_engines:
            raise AbsolidixPayloadException(message="unsupported engine", status=400)
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe,
            partial(self.create_event, data_id, engine, input),
        )
        if evt["type"] == "calculations":
            data = sorted(
                evt.get("data", {}).get("data", []),
                key=lambda x: x.get("created_at", datetime.fromordinal(1)),
            )
            return data[-1] if data else None

    async def _get_results(
        self,
        calc_getter: Callable[[], Awaitable[Optional[AbsolidixCalculationDTO]]],
        on_progress: Optional[AbsolidixCalculationOnProgressT] = None,
    ) -> Optional[Sequence[AbsolidixDataSourceDTO]]:
        "Waits for the end of the calculation and returns the results"

        def get_new_calc_id(data_id: int, calcs: Sequence[AbsolidixCalculationDTO]):
            """
            The funny part is that when the computation ends,
            we get a data source instead of a calculation.
            """
            for calc in calcs:
                if calc.get("progress", 0) < 100:
                    continue
                data = cast(AbsolidixDataSourceDTO, calc)
                if data_id in data.get("parents", []):
                    return data["id"]
            return None

        def get_calc_from_listing(
            calc_id: int, calcs: Sequence[AbsolidixCalculationDTO]
        ):
            for calc in calcs:
                if calc_id == calc["id"]:
                    return calc
            return None

        def filter_ds_for_calc(data_id: int, dss: Sequence[AbsolidixDataSourceDTO]):
            return [
                ds
                for ds in dss
                if ds["type"] in DATA_SOURCE_CALC_RESULT_TYPES
                and data_id in ds["parents"]
            ]

        async with self._root.stream.subscribe() as sub:
            target_calc = await calc_getter()
            if not target_calc:
                return  # pragma: no cover
            calc_id = target_calc["id"]
            data_id = target_calc["parent"]
            async for msg in sub:
                if msg["type"] == "calculations":
                    calc_id = get_new_calc_id(data_id, msg["data"]["data"]) or calc_id
                    target_calc = get_calc_from_listing(calc_id, msg["data"]["data"])

                    # run callback if any and exit if needed
                    if target_calc and on_progress:
                        if (
                            await on_progress(target_calc)
                            if iscoroutinefunction(on_progress)
                            else on_progress(target_calc)
                        ) is False:
                            return

                # results
                if msg["type"] == "datasources":
                    results = filter_ds_for_calc(data_id, msg["data"]["data"])
                    # if results or calc is done but no results
                    if results or target_calc is None:
                        return results

    async def get_results(
        self,
        calc_id: int,
        on_progress: Optional[AbsolidixCalculationOnProgressT] = None,
    ) -> Optional[Sequence[AbsolidixDataSourceDTO]]:
        "Waits for the end of the calculation and returns the results"

        async def get_calc():
            return await self.get(calc_id)

        return await self._get_results(get_calc, on_progress)

    async def create_get_results(
        self,
        data_id: int,
        engine: str = "dummy",
        input: Optional[str] = None,
        on_progress: Optional[AbsolidixCalculationOnProgressT] = None,
    ) -> Optional[Sequence[AbsolidixDataSourceDTO]]:
        "Create calculation, wait done and get results"

        async def get_calc():
            return await self.create(data_id, engine, input)

        return await self._get_results(get_calc, on_progress)

    @raise_on_absolidix_error
    async def get_engines(self) -> Sequence[str]:
        "Get supported calculation engines"
        msg = (
            "v0.calculations.get_engines() is deprecated; "
            "please, use calculations.supported() instead"
        )
        warn(DeprecationWarning(msg))
        return await self._root.calculations.supported()

    async def list_event(self) -> AbsolidixRequestIdDTO:
        "List all user's calculations"
        async with await self._client.request(
            method="GET",
            url=self._base_url,
            auth_required=True,
        ) as resp:
            return await resp.json(loads=absolidix_json_decoder)

    async def list(self) -> Sequence[AbsolidixCalculationDTO]:
        "List all user's calculations and wait for result"
        evt = await act_and_get_result_from_stream(
            self._root.stream.subscribe, partial(self.list_event)
        )
        if evt["type"] == "calculations":
            return evt.get("data", {}).get("data", [])
        return []  # pragma: no cover

    async def get(self, calc_id: int) -> Optional[AbsolidixCalculationDTO]:
        "Get calculation by id"
        data = list(filter(lambda x: x["id"] == calc_id, await self.list()))
        return data[-1] if data else None
