from __future__ import annotations

from discord.ext import commands


class OwnerCog(commands.Cog, command_attrs=dict(hidden=True), name="Owner"):
    """
    Commands used for managing the bot.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx) -> None:
        """Shuts the bot down."""
        await ctx.send("Goodbye!")
        await self.bot.close()


async def setup(bot) -> None:
    await bot.add_cog(OwnerCog(bot))
