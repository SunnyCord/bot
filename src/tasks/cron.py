from __future__ import annotations

import discord
from discord.ext import commands


class CronTask(commands.Cog):
    """Database maintenance task"""

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(CronTask(bot))
