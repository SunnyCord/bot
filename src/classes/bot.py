###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING

import aiohttp
import aiordr
import aiosu
import discord
import pomice
from cryptography.fernet import Fernet
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from cogs import LOAD_EXTENSIONS as COGS_LOAD
from common.crypto import check_aes
from common.helpers import get_bot_version
from common.logging import init_logging
from common.logging import logger
from common.logging import pomice_logger
from common.osudaily import OsuDailyClient
from listeners import LOAD_EXTENSIONS as LISTENER_LOAD
from models.config import ConfigList
from repository import BeatmapRepository
from repository import BeatmapsetRepository
from repository import GraphRepository
from repository import GuildSettingsRepository
from repository import OsuRepository
from repository import RecordingPreferencesRepository
from repository import StatsRepository
from repository import UserPreferencesRepository
from repository import UserRepository
from service import BeatmapService
from service import BeatmapsetService
from service import GraphService
from service import GuildSettingsService
from service import RecordingPreferencesService
from service import StatsService
from service import UserPreferencesService
from service import UserService
from tasks import LOAD_EXTENSIONS as TASKS_LOAD

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


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


def _intersect_commands(
    cog: commands.Cog,
) -> Any:
    """Gets an iterable of all (app) commands in a cog."""
    seen_commands = {}

    for cmd in cog.walk_app_commands():
        seen_commands[cmd.name] = cmd

    for cmd in cog.walk_commands():
        seen_commands[cmd.name] = cmd

    return seen_commands.values()


def _check_is_premium(cmd: commands.Command | discord.app_commands.AppCommand) -> bool:
    checks = getattr(cmd, "checks", [])
    for check in checks:
        if "premium" in check.__name__.casefold():
            return True
    return False


def _get_cogs_dict(bot: Sunny) -> dict[str, Any]:
    """Gets a dict of all cogs and their commands."""
    cogs_list: list[dict[str, Any]] = []

    for cog in bot.cogs.values():
        if getattr(cog, "hidden", True):
            continue

        cmd_list = []

        for cmd in _intersect_commands(cog):
            if getattr(cmd, "hidden", False):
                continue

            is_hybrid = isinstance(cmd, commands.HybridCommand)
            is_premium = _check_is_premium(cmd)

            cmd = getattr(cmd, "app_command", cmd)

            parameters = {p.display_name: p.description for p in cmd.parameters}
            cmd_list.append(
                {
                    "name": cmd.name,
                    "description": cmd.description,
                    "parameters": parameters,
                    "is_hybrid": is_hybrid,
                    "is_premium": is_premium,
                },
            )

        if getattr(cog, "display_parent"):
            parent = next(
                (p for p in cogs_list if p["name"] == cog.display_parent),
                None,
            )
            parent["commands"].extend(cmd_list)
            continue

        cogs_list.append(
            {
                "name": cog.qualified_name.lower(),
                "description": cog.description,
                "commands": cmd_list,
            },
        )

    return cogs_list


async def _load_extensions(bot: Sunny):
    for cog in COGS_LOAD:
        await bot.load_extension(cog)
    for listener in LISTENER_LOAD:
        await bot.load_extension(listener)
    for task in TASKS_LOAD:
        await bot.load_extension(task)


class Sunny(commands.AutoShardedBot):
    """Sunny Bot"""

    __slots__ = (
        "config",
        "database",
        "redis_client",
        "redis_pubsub",
        "pomice_node_pool",
        "version",
        "support_guild",
        "premium_role",
        "beatmap_service",
        "graph_service",
        "guild_settings_service",
        "recording_prefs_service",
        "stats_service",
        "user_prefs_service",
        "user_service",
        "osu_daily_client",
        "client_v1",
        "client_v2",
        "client_storage",
        "ordr_client",
        "aes",
    )

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
        self.version: str = "sunny?.?.?"
        self.support_guild: discord.Guild | None = None
        self.premium_role: discord.Role | None = None

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
        beatmapset_repo = BeatmapsetRepository(self.database)
        user_repo = UserRepository(self.database)
        settings_repo = GuildSettingsRepository(self.database)
        osu_repo = OsuRepository(self.database)
        user_prefs_repo = UserPreferencesRepository(self.database)
        recording_prefs_repo = RecordingPreferencesRepository(self.database)

        logger.info("Setting up services...")
        self.pomice_node_pool = pomice.NodePool()

        self.beatmap_service = BeatmapService(beatmap_repo)
        self.beatmapset_service = BeatmapsetService(beatmapset_repo)
        self.user_service = UserService(user_repo)
        self.stats_service = StatsService(stats_repo)
        self.guild_settings_service = GuildSettingsService(settings_repo)
        self.user_prefs_service = UserPreferencesService(user_prefs_repo)
        self.recording_prefs_service = RecordingPreferencesService(recording_prefs_repo)
        self.graph_service = GraphService(graph_repo)
        self.osu_daily_client = OsuDailyClient(self.config.osu_daily_key)
        self.client_v1 = aiosu.v1.Client(self.config.osu_api.api_key)
        self.client_storage = aiosu.v2.ClientStorage(
            token_repository=osu_repo,
            client_secret=self.config.osu_api.client_secret,
            client_id=self.config.osu_api.client_id,
        )
        self.ordr_client = aiordr.ordrClient(
            verification_key=self.config.ordr_key,
            limiter=(40, 60),
        )
        self.aes = Fernet(check_aes())

    async def start_pomice_nodes(self) -> None:
        if self.pomice_node_pool.node_count > 0:
            logger.debug(
                "Attempted to call start_pomice_nodes when nodes already exist!",
            )
            return

        await self.wait_until_ready()

        for node in self.config.lavalink.nodes:
            try:
                await self.pomice_node_pool.create_node(
                    bot=self,
                    host=node.host,
                    port=node.port,
                    password=node.password,
                    secure=node.ssl_enabled,
                    identifier=node.name,
                    heartbeat=node.heartbeat,
                    spotify_client_id=self.config.lavalink.spotify_client_id,
                    spotify_client_secret=self.config.lavalink.spotify_client_secret,
                    apple_music=True,
                    logger=pomice_logger,
                )
            except pomice.NodeConnectionFailure:
                logger.error(f"Failed connecting to node '{node.name}'!")

        logger.info("Voice nodes ready!")

    async def setup_hook(self) -> None:
        self.aiohttp_session = aiohttp.ClientSession()
        logger.info("Setting up modules...")
        await self.load_extension("jishaku")
        await _load_extensions(self)
        await self.stats_service.set_commands(_get_cogs_dict(self))
        self.version = await get_bot_version()
        await self.stats_service.set_bot_version(self.version)

        logger.info("Setting up support guild...")
        self.support_guild = await self.fetch_guild(
            self.config.premium.support_guild_id,
        )
        self.premium_role = self.support_guild.get_role(
            self.config.premium.premium_role_id,
        )

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.stats_service.set_cog_count(len(self.cogs))
        await self.stats_service.set_command_count(len(self.all_commands))
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.stats_service.set_user_count(len(self.users))
        await self.start_pomice_nodes()

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.info(f"Joined guild {guild.name} (ID: {guild.id})")
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.stats_service.set_user_count(len(self.users))
        await self.guild_settings_service.create(guild.id)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.info(f"Left guild {guild.name} (ID: {guild.id})")
        await self.stats_service.set_guild_count(len(self.guilds))
        await self.stats_service.set_user_count(len(self.users))
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
        await self.pomice_node_pool.disconnect()
        await self.client_v1.aclose()
        await self.client_storage.aclose()
        await self.ordr_client.aclose()
        with suppress(AttributeError):
            await self.aiohttp_session.close()
        await super().close()
