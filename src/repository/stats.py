###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from redis.asyncio import Redis


class StatsRepository:
    """Repository for statistics."""

    __slots__ = ("redis",)

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def set_command_count(self, count: int) -> None:
        """Set command count.
        Args:
            count (int): Command count.
        """
        await self.redis.set("sunny:command-count", count)

    async def set_cog_count(self, count: int) -> None:
        """Set cog count.
        Args:
            count (int): Cog count.
        """
        await self.redis.set("sunny:cog-count", count)

    async def set_guild_count(self, count: int) -> None:
        """Set guild count.
        Args:
            count (int): Guild count.
        """
        await self.redis.set("sunny:guild-count", count)

    async def set_user_count(self, count: int) -> None:
        """Set user count.
        Args:
            count (int): User count.
        """
        await self.redis.set("sunny:user-count", count)

    async def set_commands(self, commands_data: bytes) -> None:
        """Set commands.
        Args:
            commands_data (bytes): Commands JSON data.
        """
        await self.redis.set("sunny:commands", commands_data)

    async def set_bot_version(self, version: str) -> None:
        """Set bot version.
        Args:
            version (str): Bot version.
        """
        await self.redis.set("sunny:bot-version", version)
