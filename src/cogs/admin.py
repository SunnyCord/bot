from __future__ import annotations

import discord
from commons import checks
from discord.ext import commands
from pytimeparse.timeparse import timeparse


class Admin(commands.Cog):
    """
    Commands for managing Discord servers.
    """

    def __init__(self, bot):
        self.bot = bot

    @checks.can_managemsg()
    @commands.command()
    async def prune(self, ctx, count: int):
        """Deletes a specified amount of messages. (Max 100)"""
        count = max(1, min(count, 100))
        await ctx.message.channel.purge(limit=count, bulk=True)

    @checks.can_managemsg()
    @commands.command()
    async def clean(self, ctx):
        """Cleans the chat of the bot's messages."""

        def is_me(m):
            return m.author == self.bot.user

        await ctx.message.channel.purge(limit=100, check=is_me)


async def setup(bot):
    await bot.add_cog(Admin(bot))
