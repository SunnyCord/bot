###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from classes.cog import MetadataGroupCog
from classes.exceptions import WeatherAPIError
from common.weather import WeatherClient
from discord import app_commands
from discord.ext import commands
from models.weather import Units
from ui.embeds.weather import WeatherInfoEmbed


if TYPE_CHECKING:
    from classes.bot import Sunny


class Weather(MetadataGroupCog, name="weather"):
    """
    Commands for getting weather information.
    """

    __slots__ = (
        "bot",
        "weather_client",
    )

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.weather_client = WeatherClient(bot.config.open_weather_key)

    async def cog_unload(self) -> None:
        await self.weather_client.close()

    @commands.hybrid_command(
        name="info",
        description="Get the weather for a location.",
    )
    @app_commands.describe(
        location="The location to get the weather for.",
    )
    async def info_command(self, ctx: commands.Context, *, location: str) -> None:
        units = await self.bot.user_prefs_service.get_units(ctx.author.id)

        try:
            weather = await self.weather_client.get_weather(location, units)
        except WeatherAPIError as e:
            await ctx.send(f"Sorry! {e.message.capitalize()}.")
            return

        await ctx.send(embed=WeatherInfoEmbed(ctx, weather, units))

    @commands.hybrid_command(
        name="units",
        description="Set the units for weather.",
    )
    @app_commands.describe(
        units="The units to use.",
    )
    async def units_command(self, ctx: commands.Context, units: Units) -> None:
        await self.bot.user_prefs_service.set_units(ctx.author.id, units)
        await ctx.send(f"Set weather units to **{units}**.")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Weather(bot))
