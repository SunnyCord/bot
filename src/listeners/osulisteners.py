from __future__ import annotations

from io import BytesIO

import aiohttp
import commons.redisIO as redisIO
import discord
from classes.embeds.BeatmapEmbed import BeatmapEmbed
from discord.ext import commands


class OsuListeners(
    commands.Cog,
    command_attrs=dict(hidden=True),
    name="osu! Chat Listener",
):
    """osu! Message Listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        beatmap = await self.bot.osuHelpers.getBeatmapFromText(message.content, True)
        if beatmap is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://b.ppy.sh/preview/{beatmap.beatmapset_id}.mp3",
            ) as resp:
                if resp.status == 200:
                    f = BytesIO(await resp.read())

        if self.bot.config.redis is True:
            redisIO.setValue(message.channel.id, beatmap.beatmap_id)
            redisIO.setValue(f"{message.channel.id}.mode", beatmap.mode)

        await message.channel.send(
            embed=BeatmapEmbed(beatmap, self.bot.config.color),
            file=discord.File(f, filename="Preview.mp3"),
        )


async def setup(bot):
    await bot.add_cog(OsuListeners(bot))
