from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands
from models.cog import MetadataCog

if TYPE_CHECKING:
    from discord import Guild
    from models.bot import Sunny


class Settings(MetadataCog):
    """
    Commands user for changing server-based settings.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="forgetme",
        description="Deletes all of your data from the bot.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def forget_command(self, ctx: commands.Context) -> None:
        await self.bot.user_service.delete(ctx.author.id)
        await ctx.send("Your data has been successfully deleted. Sorry to see you go!")

    # async def on_guild_join(self, guild: Guild) -> None:
    #    await self.bot.mongoIO.add_guild(guild)

    # async def on_guild_leave(self, guild: Guild) -> None:
    #    await self.bot.mongoIO.remove_guild(guild)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Settings(bot))
