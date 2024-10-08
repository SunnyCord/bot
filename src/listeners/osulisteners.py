###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from contextlib import suppress
from io import BytesIO
from typing import TYPE_CHECKING

import discord
from aiosu.exceptions import APIException
from aiosu.models import User
from discord.ext import commands

from classes.cog import MetadataCog
from common import graphing
from common.helpers import get_beatmap_from_text
from common.helpers import get_user_from_text
from ui.embeds.osu import OsuProfileCompactEmbed
from ui.menus.osu import OsuBeatmapView

if TYPE_CHECKING:
    from classes.bot import Sunny


class OsuListeners(
    MetadataCog,
    name="osu! Chat Listener",
    hidden=True,
):
    """osu! Message Listeners"""

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    async def get_graph(
        self,
        user: User,
        mode_id: int,
    ) -> BytesIO | None:
        try:
            graph = await self.bot.graph_service.get_one(user.id, mode_id)
        except ValueError:
            if not user.rank_history:
                return None
            graph = await self.bot.run_blocking(graphing.plot_rank_graph, user)
            await self.bot.graph_service.add(user.id, graph, mode_id)
        return graph

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (
            message.guild
            and not await self.bot.guild_settings_service.get_listener_status(
                message.guild.id,
            )
        ):
            return
        await self.beatmap_listener(message)
        await self.user_listener(message)

    async def beatmap_listener(self, message: discord.Message) -> None:
        beatmap_data = get_beatmap_from_text(message.content, True)
        beatmapset_id = beatmap_data.get("beatmapset_id")
        beatmap_id = beatmap_data.get("beatmap_id")
        if beatmapset_id is None and beatmap_id is None:
            return

        ctx = await self.bot.get_context(message)
        client = await self.bot.client_storage.app_client

        try:
            if beatmapset_id is None:
                beatmap = await client.get_beatmap(beatmap_id)
                if beatmap is None:
                    return
                beatmapset_id = beatmap.beatmapset_id

            beatmapset = await client.get_beatmapset(beatmapset_id)
        except APIException:
            return

        async with self.bot.aiohttp_session.get(
            f"https:{beatmapset.preview_url}",
        ) as resp:
            if resp.status != 200:
                audio_file = None
            file_bytes = BytesIO(await resp.read())
            audio_file = discord.File(file_bytes, filename="Preview.mp3")

        if len(beatmapset.beatmaps) == 0:
            return

        await self.bot.beatmap_service.add(ctx.channel.id, beatmapset.beatmaps[0])
        with suppress(discord.Forbidden):
            await OsuBeatmapView.start(
                ctx,
                beatmapset,
                file=audio_file,
            )

    async def user_listener(self, message: discord.Message) -> None:
        user_id = get_user_from_text(message.content)
        if user_id is None:
            return

        ctx = await self.bot.get_context(message)

        client = await self.bot.client_storage.app_client

        try:
            user = await client.get_user(user_id)
        except APIException:
            return

        embed = OsuProfileCompactEmbed(ctx, user, user.playmode)
        embed.set_image(url="attachment://rank_graph.png")
        args = {
            "embed": embed,
        }

        with suppress(ValueError):
            graph = await self.get_graph(user, int(user.playmode))
            if graph:
                args["file"] = discord.File(graph, "rank_graph.png")

        with suppress(discord.Forbidden):
            await ctx.send(**args)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuListeners(bot))
