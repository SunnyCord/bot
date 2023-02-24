from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import aiohttp
import discord
from classes.cog import MetadataCog
from common.helpers import get_beatmap_from_text
from discord.ext import commands
from ui.menus.osu import OsuBeatmapView

if TYPE_CHECKING:
    from classes.bot import Sunny


class OsuListeners(
    MetadataCog,
    name="osu! Chat Listener",
    hidden=True,
):
    """osu! Message Listeners"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self.beatmap_listener(message)

    async def beatmap_listener(self, message: discord.Message) -> None:
        beatmap_data = get_beatmap_from_text(message.content, True)
        beatmapset_id = beatmap_data.get("beatmapset_id")
        beatmap_id = beatmap_data.get("beatmap_id")
        if beatmapset_id is None and beatmap_id is None:
            return

        client = await self.bot.client_storage.app_client

        if beatmapset_id is None:
            beatmap = await client.get_beatmap(beatmap_id)
            if beatmap is None:
                return
            beatmapset_id = beatmap.beatmapset_id

        beatmapset = await client.get_beatmapset(beatmapset_id)
        if beatmapset is None:
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https:{beatmapset.preview_url}") as resp:
                if resp.status != 200:
                    return
                audio_file = BytesIO(await resp.read())

        await OsuBeatmapView.start(
            message,
            self.bot,
            beatmapset,
            file=discord.File(audio_file, filename="Preview.mp3"),
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuListeners(bot))
