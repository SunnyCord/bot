###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import async_timeout
from classes.cog import MetadataCog
from discord.ext import tasks

if TYPE_CHECKING:
    from classes.bot import Sunny
    from typing import Callable


class CronTask(MetadataCog, hidden=True):
    """Database maintenance task"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.pubsub_task.start()

        self.handlers: dict[str, Callable] = {}

    def cog_unload(self) -> None:
        self.pubsub_task.cancel()

    async def handle_message(self, message: dict[str, str]) -> None:
        channel = message["channel"]
        data = message["data"]
        if handler := self.handlers.get(channel):
            await handler(data)

    @tasks.loop(seconds=0.5)
    async def pubsub_task(self) -> None:
        async with async_timeout.timeout(1):
            message = await self.bot.redis_pubsub.get_message()
            if message is not None:
                await self.handle_message(message)

    @pubsub_task.before_loop
    async def before_pubsub_task(self) -> None:
        await self.bot.wait_until_ready()
        await self.bot.redis_pubsub.psubscribe("sunny:*")


async def setup(bot: Sunny) -> None:
    return  # Disabled for now
    await bot.add_cog(CronTask(bot))
