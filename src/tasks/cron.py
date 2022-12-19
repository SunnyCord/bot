from __future__ import annotations

from typing import TYPE_CHECKING

import async_timeout
import orjson
from discord.ext import commands
from discord.ext import tasks

if TYPE_CHECKING:
    from classes.bot import Sunny


class CronTask(commands.Cog):
    """Database maintenance task"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.redis = self.bot.redisIO
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        self.client_storage = self.bot.client_storage
        self.pubsub_task.start()
        self.update_task.start()

        self.handlers = {
            "sunny:stat-refresh": self.update_stats,
            "sunny:oauth-process": self.process_token,
        }

    def cog_unload(self) -> None:
        self.pubsub_task.cancel()
        self.update_task.cancel()

    async def process_token(self, data: bytes) -> None:
        unpacked_data = orjson.loads(data)
        print(unpacked_data)

    async def update_stats(self, data: str) -> None:
        await self.redis.set("sunny:guild-count", len(self.bot.guilds))
        await self.redis.set("sunny:command-count", len(self.bot.commands))

    async def handle_message(self, message: dict[str, str]) -> None:
        channel = message.get("channel")
        data = message.get("data")
        if handler := self.handlers.get(channel):
            await handler(data)

    @tasks.loop(seconds=0.5)
    async def pubsub_task(self) -> None:
        async with async_timeout.timeout(1):
            message = await self.pubsub.get_message()
            if message is not None:
                await self.handle_message(message)

    @tasks.loop(minutes=720)
    async def update_task(self) -> None:
        ...

    @pubsub_task.before_loop
    async def before_pubsub_task(self) -> None:
        await self.bot.wait_until_ready()
        await self.pubsub.psubscribe("sunny:*")

    @update_task.before_loop
    async def before_update_task(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CronTask(bot))
