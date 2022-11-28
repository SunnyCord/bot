from __future__ import annotations

import discord
from discord.ext import commands


class OwnerCog(commands.Cog, command_attrs=dict(hidden=True), name="Owner"):
    """
    Commands used for managing the bot.
    """

    def __init__(self, bot) -> None:
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
    async def rebuild_command(self, ctx: commands.Context, *, args="normal") -> None:
        """Rebuilds the database. (Owner-only)"""
        start_time = time.time()
        await self.bot.mongoIO.wipe()
        servers = list(self.bot.guilds)
        args = args.lower()
        for x in range(len(servers)):
            if args == "debug":
                print(f"Adding server {servers[x-1].name}")
            await self.bot.mongoIO.addServer(servers[x - 1])
            for member in servers[x - 1].members:
                if not member.bot and not await self.bot.mongoIO.userExists(member):
                    if args == "debug":
                        print(f"Adding member {member.name}")
                    await self.bot.mongoIO.addUser(member)
        await ctx.send(f"Done rebuilding. {time.time() - start_time}s")

    @commands.is_owner()
    @commands.command(
        name="blacklist",
        description="Blacklists a user from the bot",
        hidden=True,
    )
    async def blacklist_command(self, ctx: commands.Context, user: discord.Member):
        if not await self.bot.mongoIO.userExists(user):
            await self.bot.mongoIO.addUser(user, True)
        else:
            await self.bot.mongoIO.blacklistUser(user)
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
        await self.bot.mongoIO.unblacklistUser(user)
        await ctx.send("User unblacklisted.")


async def setup(bot) -> None:
    await bot.add_cog(OwnerCog(bot))
