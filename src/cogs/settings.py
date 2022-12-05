from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from discord import Guild
    from classes.bot import Sunny


class Settings(commands.Cog):
    """
    Commands user for changing server-based settings.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def forgetme(self, ctx: commands.Context) -> None:
        await self.bot.mongoIO.removeUser(ctx.author)
        await ctx.send("Your data has been successfully deleted. Sorry to see you go!")

    async def on_guild_join(self, guild: Guild) -> None:
        await self.bot.mongoIO.addServer(guild)

    async def on_guild_leave(self, guild: Guild) -> None:
        await self.bot.mongoIO.removeServer(guild)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Settings(bot))
