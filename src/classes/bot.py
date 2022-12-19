from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import aiosu
import discord
import orjson
from classes.config import ConfigList
from commons.helpers import list_module
from commons.mongoIO import mongoIO
from commons.redisIO import redisIO
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

if TYPE_CHECKING:
    from typing import Any
    from typing import Optional

logger = logging.getLogger()


async def _get_prefix(bot: Sunny, message: discord.Message) -> list[str]:
    """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
    return commands.when_mentioned_or(*bot.config.command_prefixes)(bot, message)


def _get_intents() -> discord.Intents:
    return discord.Intents().default() | discord.Intents(
        members=True,
        message_content=True,
    )


class Sunny(commands.AutoShardedBot):
    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")

        module_folders = ["listeners", "cogs", "tasks"]
        for module in module_folders:
            for extension in list_module(module):
                name = f"{module}.{os.path.splitext(extension)[0]}"
                await self.load_extension(name)
                # except Exception as e:
                #    logging.error(f"Failed loading module {name} : {e}")

    def __init__(self, **kwargs: Any) -> None:
        activity = discord.Activity(type=discord.ActivityType.watching, name="you.")
        super().__init__(
            description="Sunny Bot",
            command_prefix=_get_prefix,
            intents=_get_intents(),
            activity=activity,
            help_command=None,
        )
        self.config = ConfigList.get_config()
        self.motorClient: AsyncIOMotorClient = AsyncIOMotorClient(
            self.config.mongo.host,
            serverSelectionTimeoutMS=self.config.mongo.timeout,
        )
        self.redisIO: Optional[redisIO] = (
            redisIO(self) if self.config.redis.enable else None
        )
        self.mongoIO: mongoIO = mongoIO(self)
        self.client_v1 = aiosu.v1.Client(self.config.osuAPI)
        self.client_storage = aiosu.v2.ClientStorage()

    def get_cogs_dict(self) -> dict[str, Any]:
        """Gets a dict of all cogs and their commands."""
        cogs_dict = {}
        for cog_name, cog in self.cogs.items():
            if getattr(cog, "hidden", True):
                continue

            commands_dict = {}
            for cmd in cog.get_commands() + cog.get_app_commands():
                if getattr(cmd, "hidden", False):
                    continue
                cmd = getattr(cmd, "app_command", cmd)

                parameters = {p.display_name: p.description for p in cmd.parameters}
                commands_dict[cmd.name] = {
                    "name": cmd.name,
                    "description": cmd.description,
                    "parameters": parameters,
                }

            if getattr(cog, "display_parent"):
                parent = cogs_dict[cog.display_parent]
                parent["commands"].update(commands_dict)
                continue

            cogs_dict[cog.qualified_name.lower()] = {
                "description": cog.description,
                "commands": commands_dict,
            }

        return cogs_dict

    async def on_ready(self):
        cogs_dict = self.get_cogs_dict()
        cogs_dict_packed = orjson.dumps(cogs_dict)
        await self.redisIO.set("sunny:commands", cogs_dict_packed)

    async def on_message(self, message: discord.Message) -> None:
        ignore = not message.guild
        ignore |= message.author.bot
        ignore |= not self.is_ready()
        ignore |= await self.mongoIO.is_blacklisted(message.author)
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
