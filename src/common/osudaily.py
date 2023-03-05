###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import functools
from typing import Any
from typing import Callable

import orjson
from aiohttp import ClientSession


def prepare_client(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(self: OsuDailyClient, *args: Any, **kwargs: Any) -> Any:
        if not self._session:
            self._session = ClientSession()
        return await func(self, *args, **kwargs)

    return wrapper


class OsuDailyClient:
    __slots__ = (
        "__key",
        "_session",
    )

    def __init__(self, key: str):
        self.__key = key
        self._session: ClientSession = None

    async def __aenter__(self) -> OsuDailyClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    @prepare_client
    async def get_closest_rank(self, pp: int, mode_int: int) -> int:
        params = {
            "k": self.__key,
            "t": "pp",
            "v": pp,
            "m": mode_int,
        }
        async with self._session.get(
            "https://osudaily.net/api/pp.php",
            params=params,
        ) as resp:
            return orjson.loads(await resp.read())["rank"]

    @prepare_client
    async def get_closest_pp(self, rank: int, mode_int: int) -> float:
        params = {
            "k": self.__key,
            "t": "rank",
            "v": rank,
            "m": mode_int,
        }
        async with self._session.get(
            "https://osudaily.net/api/pp.php",
            params=params,
        ) as resp:
            return orjson.loads(await resp.read())["pp"]

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
