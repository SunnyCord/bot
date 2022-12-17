from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import aiohttp
import discord
from commons.helpers import get_beatmap_from_text
from discord.ext import commands
from ui.embeds.osu import OsuBeatmapEmbed

if TYPE_CHECKING:
    from classes.bot import Sunny


class OsuListeners(
    commands.Cog,
    command_attrs=dict(hidden=True),
    name="osu! Chat Listener",
):  # type: ignore
    """osu! Message Listeners"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        beatmap_data = get_beatmap_from_text(message.content, True)
        filtered_data = {k: v for k, v in beatmap_data.items() if v is not None}
        if not filtered_data:
            return

        beatmapset = (await self.bot.client_v1.get_beatmap(**filtered_data))[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(beatmapset.preview_url) as resp:
                if resp.status != 200:
                    return
                f = BytesIO(await resp.read())

        beatmap = beatmapset.beatmaps[0]
        if self.bot.redisIO is not None:
            self.bot.redisIO.set_value(message.channel.id, beatmap.id)
            self.bot.redisIO.set_value(f"{message.channel.id}.mode", beatmap.mode.id)

        await message.channel.send(
            embed=OsuBeatmapEmbed(beatmapset, color=self.bot.config.color),
            file=discord.File(f, filename="Preview.mp3"),
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuListeners(bot))
