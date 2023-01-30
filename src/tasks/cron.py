from __future__ import annotations

from typing import TYPE_CHECKING

import async_timeout
import orjson
from aiosu.models import OAuthToken
from discord.ext import tasks
from models.cog import MetadataCog

if TYPE_CHECKING:
    from models.bot import Sunny


class CronTask(MetadataCog, hidden=True):
    """Database maintenance task"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.client_storage = self.bot.client_storage
        self.client_storage.on_client_add(self.on_client_add)
        self.pubsub_task.start()
        self.update_task.start()

        self.handlers = {
            "sunny:oauth-process": self.process_token,
        }

    def cog_unload(self) -> None:
        self.pubsub_task.cancel()
        self.update_task.cancel()

    async def on_client_add(self, event):
        discord_id = event.client_id
        client = event.client
        token = client.token
        print(token)

    async def process_token(self, data: bytes) -> None:
        unpacked_data = orjson.loads(data)
        token = OAuthToken.parse_obj(unpacked_data["token"])
        discord_id = unpacked_data["state"]
        await self.client_storage.add_client(token, id=discord_id)

    async def handle_message(self, message: dict[str, str]) -> None:
        channel = message.get("channel")
        data = message.get("data")
        if handler := self.handlers.get(channel):
            await handler(data)

    @tasks.loop(seconds=0.5)
    async def pubsub_task(self) -> None:
        async with async_timeout.timeout(1):
            message = await self.bot.redis_pubsub.get_message()
            if message is not None:
                await self.handle_message(message)

    @tasks.loop(minutes=720)
    async def update_task(self) -> None:
        ...

    @pubsub_task.before_loop
    async def before_pubsub_task(self) -> None:
        await self.bot.wait_until_ready()
        await self.bot.redis_pubsub.psubscribe("sunny:*")

    @update_task.before_loop
    async def before_update_task(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CronTask(bot))
