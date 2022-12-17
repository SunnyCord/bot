from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from classes.bot import Sunny


class CronTask(commands.Cog):
    """Database maintenance task"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    # tasks.loop


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CronTask(bot))
