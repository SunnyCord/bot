from __future__ import annotations

import logging
import os

import aiosu
import discord
from classes.config import ConfigList
from commons.helpers import list_module
from commons.mongoIO import mongoIO
from commons.redisIO import redisIO
from discord.ext import commands
from motor import motor_asyncio

logger = logging.getLogger()


class Sunny(commands.AutoShardedBot):
    async def setup_hook(self):
        await self.load_extension("jishaku")

        module_folders = ["listeners", "cogs", "tasks"]
        for module in module_folders:
            for extension in list_module(module):
                name = f"{module}.{os.path.splitext(extension)[0]}"
                # try:
                await self.load_extension(name)
                # except Exception as e:
                #    logging.error(f"Failed loading module {name} : {e}")

    @staticmethod
    async def __get_prefix(self, message):
        """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
        return commands.when_mentioned_or(*self.config.command_prefixes)(self, message)

    def __init__(self, **kwargs) -> None:
        super().__init__(
            description="Sunny Bot",
            command_prefix=self.__get_prefix,
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

    async def on_message(self, msg):
        ignore = not msg.guild
        ignore |= msg.author.bot
        ignore |= not self.is_ready()
        ignore |= await self.mongoIO.isBlacklisted(msg.author)
        if ignore:
            return
        await self.process_commands(msg)

    async def is_owner(self, user: discord.User):
        if user.id in self.config.owners:
            return True
        # Else fall back to the original
        return await super().is_owner(user)

    def run(self, **kwargs) -> None:
        super().run(self.config.token, log_level=self.config.log_level, **kwargs)
