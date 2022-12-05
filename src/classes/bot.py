from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import aiosu
import discord
from classes.config import ConfigList
from commons.helpers import list_module
from commons.mongoIO import mongoIO
from commons.redisIO import redisIO
from discord.ext import commands
from motor import motor_asyncio

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger()


async def __get_prefix(bot: Sunny, message: discord.Message) -> list[str]:
    """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
    return commands.when_mentioned_or(*bot.config.command_prefixes)(bot, message)


class Sunny(commands.AutoShardedBot):
    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")

        module_folders = ["listeners", "cogs", "tasks"]
        for module in module_folders:
            for extension in list_module(module):
                name = f"{module}.{os.path.splitext(extension)[0]}"
                try:
                    await self.load_extension(name)
                except Exception as e:
                    logging.error(f"Failed loading module {name} : {e}")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            description="Sunny Bot",
            command_prefix=__get_prefix,
            intents=discord.Intents.all(),
            # activity=discord.Activity(),
            help_command=None,
        )
        self.config = ConfigList.get_config()
        self.motorClient = motor_asyncio.AsyncIOMotorClient(
            self.config.mongo.host,
            serverSelectionTimeoutMS=self.config.mongo.timeout,
        )
        self.redisIO = None if self.config.redis.enable else redisIO(self)
        self.mongoIO = mongoIO(self)
        self.client_v1 = aiosu.v1.Client(self.config.osuAPI)
        self.client_storage = aiosu.v2.ClientStorage()

    async def on_message(self, message: discord.Message) -> None:
        ignore = not message.guild
        ignore |= message.author.bot
        ignore |= not self.is_ready()
        ignore |= await self.mongoIO.isBlacklisted(message.author)
        if ignore:
            return
        await self.process_commands(message)

    async def is_owner(self, user: discord.User) -> bool:
        if user.id in self.config.owners:
            return True
        # Else fall back to the original
        return await super().is_owner(user)

    def run(self, **kwargs: Any) -> None:
        super().run(self.config.token, log_level=self.config.log_level, **kwargs)
