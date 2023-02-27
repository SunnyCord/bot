###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import os
from functools import partial
from typing import TYPE_CHECKING

import aiordr
import aiosu
import discord
import pomice
from common.crypto import check_aes
from common.logging import init_logging
from common.logging import logger
from cryptography.fernet import Fernet
from discord.ext import commands
from models.config import ConfigList
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from repository import BeatmapRepository
from repository import GraphRepository
from repository import GuildSettingsRepository
from repository import OsuRepository
from repository import RecordingPreferencesRepository
from repository import StatsRepository
from repository import UserPreferencesRepository
from repository import UserRepository
from service import BeatmapService
from service import GraphService
from service import GuildSettingsService
from service import RecordingPreferencesService
from service import StatsService
from service import UserPreferencesService
from service import UserService

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable


MODULE_FOLDERS = ["listeners", "cogs", "tasks"]


async def _get_prefix(bot: Sunny, message: discord.Message) -> list[str]:
    """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
    if not message.guild:
        return bot.config.command_prefixes

    prefix = await bot.guild_settings_service.get_prefix(message.guild.id)

    if not prefix:
        return commands.when_mentioned_or(*bot.config.command_prefixes)(bot, message)

    return commands.when_mentioned_or(prefix, *bot.config.command_prefixes)(
        bot,
        message,
    )


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
        init_logging(self.config.log_level)
        self.setup_db()
        self.setup_services()

    def setup_db(self) -> None:
        logger.info("Setting up database connections...")
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
        logger.info("Setting up repositories...")

        beatmap_repo = BeatmapRepository(self.redis_client)
        stats_repo = StatsRepository(self.redis_client)
        graph_repo = GraphRepository(self.redis_client)
        user_repo = UserRepository(self.database)
        settings_repo = GuildSettingsRepository(self.database)
        osu_repo = OsuRepository(self.database)
        user_prefs_repo = UserPreferencesRepository(self.database)
        recording_prefs_repo = RecordingPreferencesRepository(self.database)

        logger.info("Setting up services...")
        self.pomice_node_pool = pomice.NodePool()

        self.beatmap_service = BeatmapService(beatmap_repo)
        self.user_service = UserService(user_repo)
        self.stats_service = StatsService(stats_repo)
        self.guild_settings_service = GuildSettingsService(settings_repo)
        self.user_prefs_service = UserPreferencesService(user_prefs_repo)
        self.recording_prefs_service = RecordingPreferencesService(recording_prefs_repo)
        self.graph_service = GraphService(graph_repo)
        self.client_v1 = aiosu.v1.Client(self.config.osu_api.api_key)
        self.stable_storage = aiosu.v2.ClientStorage(
            token_repository=osu_repo,
            client_secret=self.config.osu_api.client_secret,
            client_id=self.config.osu_api.client_id,
        )
        self.lazer_storage = aiosu.v2.ClientStorage(
            token_repository=osu_repo,
            client_secret=self.config.osu_api.client_secret,
            client_id=self.config.osu_api.client_id,
            base_url="https://lazer.ppy.sh",
        )
        self.ordr_client = aiordr.ordrClient(
            verification_key=self.config.ordr_key,
            limiter=(40, 60),
        )
        self.aes = Fernet(check_aes())

    async def start_pomice_nodes(self) -> None:
        await self.wait_until_ready()

        for node_config in self.config.lavalink:
            logger.info(f"Adding node '{node_config.name}'...")
            try:
                await self.pomice_node_pool.create_node(
                    bot=self,
                    host=node_config.host,
                    port=node_config.port,
                    password=node_config.password,
                    secure=node_config.ssl_enabled,
                    identifier=node_config.name,
                )
                logger.info(f"Connected to node '{node_config.name}`")
            except pomice.NodeConnectionFailure:
                logger.error(f"Failed connecting to node '{node_config.name}'!")

        logger.info("Voice nodes ready!")

    async def setup_hook(self) -> None:
        logger.info("Setting up modules...")
        await self.load_extension("jishaku")
        await _load_extensions(self)
        await self.stats_service.set_commands(_get_cogs_dict(self))

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.start_pomice_nodes()
        await self.stats_service.set_cog_count(len(self.cogs))
        await self.stats_service.set_command_count(len(self.all_commands))
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.stats_service.set_user_count(len(self.users))

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.info(f"Joined guild {guild.name} (ID: {guild.id})")
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.guild_settings_service.create(guild.id)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.info(f"Left guild {guild.name} (ID: {guild.id})")
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.guild_settings_service.delete(guild.id)

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

    async def run_blocking(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        return await self.loop.run_in_executor(None, partial(func, *args, **kwargs))

    def run(self, **kwargs: Any) -> None:
        super().run(self.config.token, log_handler=None, **kwargs)

    async def close(self) -> None:
        await self.client_v1.close()
        await self.stable_storage.close()
        await self.lazer_storage.close()
        await self.ordr_client.close()
        await super().close()
