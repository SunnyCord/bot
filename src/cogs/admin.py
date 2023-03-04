###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from classes.cog import MetadataCog
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from classes.bot import Sunny


class Admin(MetadataCog):
    """
    Commands for managing Discord servers.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command(
        name="prune",
        description="Deletes a specified amount of messages",
    )
    @app_commands.describe(count="The number of messages to delete")
    async def prune_command(
        self,
        ctx: commands.Context,
        count: commands.Range[int, 1, 100],
    ) -> None:
        await ctx.defer(ephemeral=True)
        resp = await ctx.channel.purge(limit=count, bulk=True)
        await ctx.send(f"Deleted {len(resp)} messages.", delete_after=5)

    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command(
        name="clean",
        description="Cleans the chat of the bot's messages",
    )
    async def clean_command(self, ctx: commands.Context) -> None:
        def is_me(m: discord.Message) -> bool:
            return m.author == self.bot.user

        await ctx.defer(ephemeral=True)
        resp = await ctx.channel.purge(limit=100, check=is_me)
        await ctx.send(f"Deleted {len(resp)} messages.", delete_after=5)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Admin(bot))
