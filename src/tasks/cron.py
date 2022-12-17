from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands
from discord.ext import tasks

if TYPE_CHECKING:
    from classes.bot import Sunny


class CronTask(commands.Cog):
    """Database maintenance task"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.update.start()

    def cog_unload(self) -> None:
        self.update.cancel()

    @tasks.loop(minutes=720)
    async def update(self) -> None:
        ...

    @update.before_loop
    async def before_update(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CronTask(bot))
