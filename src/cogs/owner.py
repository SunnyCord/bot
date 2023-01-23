from __future__ import annotations

import time
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from models.cog import MetadataCog

if TYPE_CHECKING:
    from models.bot import Sunny


class OwnerCog(MetadataCog, name="Owner", hidden=True):  # type: ignore
    """
    Commands used for managing the bot.
    """

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

    # TODO rewrite with subcommands
    @commands.is_owner()
    @commands.command(name="rebuild", hidden=True)
    async def rebuild_command(
        self, ctx: commands.Context, *, args: str = "normal"
    ) -> None:
        """Rebuilds the database. (Owner-only)"""
        start_time = time.perf_counter()
        await self.bot.mongoIO.wipe()
        servers = list(self.bot.guilds)
        args = args.lower()
        for x in range(len(servers)):
            if args == "debug":
                print(f"Adding server {servers[x-1].name}")
            await self.bot.mongoIO.add_guild(servers[x - 1])
            for member in servers[x - 1].members:
                if not member.bot and not await self.bot.mongoIO.user_exists(member):
                    if args == "debug":
                        print(f"Adding member {member.name}")
                    await self.bot.mongoIO.add_user(member)
        await ctx.send(f"Done rebuilding. {time.perf_counter() - start_time}s")

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
        if not await self.bot.mongoIO.user_exists(user):
            await self.bot.mongoIO.add_user(user, True)
        else:
            await self.bot.mongoIO.blacklist_user(user)
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
        await self.bot.mongoIO.unblacklist_user(user)
        await ctx.send("User unblacklisted.")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OwnerCog(bot))
