###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field

TEMP_STRINGS = {
    "metric": "°C",
    "imperial": "°F",
}

SPEED_STRINGS = {
    "metric": "m/s",
    "imperial": "mph",
}

PRESSURE_STRINGS = {
    "metric": "hPa",
    "imperial": "hPa",
}


class Units(Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

    def __str__(self) -> str:
        return self.value

    @property
    def temperature(self) -> str:
        return TEMP_STRINGS[self.value]

    @property
    def speed(self) -> str:
        return SPEED_STRINGS[self.value]

    @property
    def pressure(self) -> str:
        return PRESSURE_STRINGS[self.value]


class Coords(BaseModel):
    lat: float
    lon: float


class WeatherItem(BaseModel):
    id: int
    main: str
    description: str
    icon: str

    @property
    def icon_url(self) -> str:
        return f"https://openweathermap.org/img/wn/{self.icon}@2x.png"


class Weather(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class Wind(BaseModel):
    speed: float
    deg: int


class Clouds(BaseModel):
    all: int


class LocationData(BaseModel):
    id: int | None = None
    type: int | None = None
    country: str
    sunrise: datetime
    sunset: datetime


class WeatherResponse(BaseModel):
    id: int
    name: str
    base: str
    coord: Coords
    items: list[WeatherItem] = Field(alias="weather")
    weather: Weather = Field(alias="main")
    location_data: LocationData = Field(alias="sys")
    time: datetime = Field(alias="dt")
    timezone: int
    visibility: int
    wind: Wind
    clouds: Clouds
    cod: int

    @property
    def url(self) -> str:
        return f"https://openweathermap.org/city/{self.id}"
