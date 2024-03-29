###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from inspect import cleandoc
from typing import TYPE_CHECKING

from discord.utils import format_dt
from emojiflags import lookup

from models.weather import Units
from models.weather import WeatherResponse
from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from discord import commands


class WeatherInfoEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, response: WeatherResponse, units: Units):
        latest_forecast = response.items[0]
        description = cleandoc(
            f"""
            {latest_forecast.main.capitalize()} ({latest_forecast.description})
            Sunrise {format_dt(response.location_data.sunrise, style="t")}
            Sunset {format_dt(response.location_data.sunset, style="t")}
            """,
        )
        flag = lookup.lookup(response.location_data.country)

        super().__init__(
            ctx,
            title=f"The current weather for {response.name} {flag}",
            description=description,
            url=response.url,
        )

        self.set_thumbnail(url=latest_forecast.icon_url)

        self.add_field(
            name="Temperature",
            value=f"{response.weather.temp}{units.temperature}",
        )
        self.add_field(
            name="Feels Like",
            value=f"{response.weather.feels_like}{units.temperature}",
        )

        self.add_field(name="", value="", inline=False)

        self.add_field(
            name="Humidity",
            value=f"{response.weather.humidity}%",
        )
        self.add_field(
            name="Cloudiness",
            value=f"{response.clouds.all}%",
        )

        self.add_field(name="", value="", inline=False)

        self.add_field(
            name="Pressure",
            value=f"{response.weather.pressure} {units.pressure}",
        )
        self.add_field(
            name="Wind Speed",
            value=f"{response.wind.speed} {units.speed}",
        )
