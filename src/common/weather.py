###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import aiohttp
import orjson
from classes.exceptions import WeatherAPIError
from models.weather import Units
from models.weather import WeatherResponse


class WeatherClient:
    __slots__ = (
        "_api_key",
        "_session",
    )

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._session = None

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        if not self._session:
            self._session = aiohttp.ClientSession()

        async with self._session.request(method, url, **kwargs) as resp:
            data = orjson.loads(await resp.read())
            if "cod" in data and data["cod"] != 200:
                raise WeatherAPIError(data["message"])

            return data

    async def get_weather(self, location: str, units: Units) -> WeatherResponse:
        params = {
            "q": location,
            "appid": self._api_key,
            "units": str(units),
        }
        data = await self._request(
            "GET",
            "https://api.openweathermap.org/data/2.5/weather",
            params=params,
        )
        return WeatherResponse.model_validate(data)

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
