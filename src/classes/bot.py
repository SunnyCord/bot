from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import aiosu
import discord
from common.crypto import check_aes
from cryptography.fernet import Fernet
from discord.ext import commands
from models.config import ConfigList
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from repository import *
from service import *

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger()

MODULE_FOLDERS = ["listeners", "cogs", "tasks"]


async def _get_prefix(bot: Sunny, message: discord.Message) -> list[str]:
    """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
    return commands.when_mentioned_or(*bot.config.command_prefixes)(bot, message)


def _get_intents() -> discord.Intents:
    return discord.Intents().default() | discord.Intents(
        members=True,
        message_content=True,
    )


def _get_cogs_dict(bot: Sunny) -> dict[str, Any]:
    """Gets a dict of all cogs and their commands."""
    cogs_dict: dict[str, Any] = {}
    for cog in bot.cogs.values():
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


def _get_modules(folder: str):
    for file in os.listdir(f"./{folder}"):
        if file.endswith(".py"):
            yield file


async def _load_extensions(bot: Sunny):
    for folder in MODULE_FOLDERS:
        for extension in _get_modules(folder):
            name = f"{folder}.{os.path.splitext(extension)[0]}"
            await bot.load_extension(name)


class Sunny(commands.AutoShardedBot):
    """Sunny Bot"""

    def __init__(self, **kwargs: Any) -> None:
        activity = discord.Activity(type=discord.ActivityType.watching, name="you.")
        super().__init__(
            description="Sunny Bot",
            command_prefix=_get_prefix,
            intents=_get_intents(),
            activity=activity,
            help_command=None,
            **kwargs,
        )
        self.config = ConfigList.get_config()
        self.setup_db()
        self.setup_services()

    def setup_db(self) -> None:
        motor_client = AsyncIOMotorClient(
            self.config.mongo.host,
            serverSelectionTimeoutMS=self.config.mongo.timeout,
        )
        self.database = motor_client[self.config.mongo.database]
        self.redis_client = Redis(
            host=self.config.redis.host,
            port=self.config.redis.port,
        )
        self.redis_pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)

    def setup_services(self) -> None:
        beatmap_repo = BeatmapRepository(self.redis_client)
        stats_repo = StatsRepository(self.redis_client)
        user_repo = UserRepository(self.database)
        settings_repo = SettingsRepository(self.database)
        osu_repo = OsuRepository(self.database)
        self.beatmap_service = BeatmapService(beatmap_repo)
        self.user_service = UserService(user_repo)
        self.stats_service = StatsService(stats_repo)
        self.settings_service = SettingsService(settings_repo)
        self.client_v1 = aiosu.v1.Client(self.config.osuAPI)
        self.client_storage = aiosu.v2.ClientStorage(
            token_repository=osu_repo,
            client_secret=self.config.osuAPIv2.client_secret,
            client_id=self.config.osuAPIv2.client_id,
        )
        self.aes = Fernet(check_aes())

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await _load_extensions(self)
        await self.stats_service.set_commands(_get_cogs_dict(self))

    async def on_ready(self) -> None:
        await self.stats_service.set_cog_count(len(self.cogs))
        await self.stats_service.set_command_count(len(self.all_commands))
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.stats_service.set_user_count(len(self.users))

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.settings_service.create(guild.id)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.settings_service.delete(guild.id)

    async def on_message(self, message: discord.Message) -> None:
        ignore = not message.guild
        ignore |= message.author.bot
        ignore |= not self.is_ready()
        ignore |= await self.user_service.is_blacklisted(message.author.id)
        if ignore:
            return
        await self.process_commands(message)

    async def is_owner(self, user: discord.User) -> bool:
        if user.id in self.config.owners:
            return True
        return await super().is_owner(user)

    def run(self, **kwargs: Any) -> None:
        super().run(self.config.token, log_level=self.config.log_level, **kwargs)
