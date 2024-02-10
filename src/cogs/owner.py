###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from classes.cog import MetadataCog

if TYPE_CHECKING:
    from classes.bot import Sunny


class Owner(MetadataCog, name="Owner", hidden=True):
    """
    Commands used for managing the bot.
    """

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="sync", hidden=True)
    async def sync_commands(self, ctx: commands.Context) -> None:
        resp = await self.bot.tree.sync()
        await ctx.send(f"Syncing slash commands. {len(resp)}")

    @commands.is_owner()
    @commands.command(name="shutdown", hidden=True)
    async def shutdown_command(self, ctx: commands.Context) -> None:
        """Shuts the bot down."""
        await ctx.send("Goodbye!")
        await self.bot.close()

    @commands.is_owner()
    @commands.command(
        name="blacklist",
        description="Blacklists a user from the bot",
        hidden=True,
    )
    async def blacklist_command(
        self,
        ctx: commands.Context,
        user: discord.Member,
    ) -> None:
        await self.bot.user_service.blacklist(user.id)
        await ctx.send("User blacklisted.")

    @commands.is_owner()
    @commands.command(
        name="unblacklist",
        description="Unblacklists a user from the bot",
        hidden=True,
    )
    async def unblacklist_command(
        self,
        ctx: commands.Context,
        user: discord.Member,
    ) -> None:
        await self.bot.user_service.unblacklist(user.id)
        await ctx.send("User unblacklisted.")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Owner(bot))
