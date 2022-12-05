from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
import discord
from discord.ext import commands

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
        """
        beatmap = await self.bot.osuHelpers.getBeatmapFromText(message.content, True)
        if beatmap is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://b.ppy.sh/preview/{beatmap.beatmapset_id}.mp3",
            ) as resp:
                if resp.status == 200:
                    f = BytesIO(await resp.read())

        if self.bot.redisIO is not None:
            self.bot.redisIO.setValue(message.channel.id, beatmap.beatmap_id)
            self.bot.redisIO.setValue(f"{message.channel.id}.mode", beatmap.mode)

        await message.channel.send(
            embed=BeatmapEmbed(beatmap, self.bot.config.color),
            file=discord.File(f, filename="Preview.mp3"),
        )
        """


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuListeners(bot))
