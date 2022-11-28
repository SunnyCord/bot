from __future__ import annotations

import discord
from discord.ext import commands


class Settings(commands.Cog):
    """
    Commands user for changing server-based settings.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def forgetme(self, ctx):
        await self.bot.mongoIO.removeUser(ctx.author)
        await ctx.send("Your data has been successfully deleted. Sorry to see you go!")

    async def on_guild_join(self, guild):
        await self.bot.mongoIO.addServer(guild)

    async def on_guild_leave(self, guild):
        await self.bot.mongoIO.removeServer(guild)


async def setup(bot):
    await bot.add_cog(Settings(bot))
