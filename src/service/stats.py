###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from repository import StatsRepository


class StatsService:
    """Service for statistics."""

    def __init__(self, repository: StatsRepository) -> None:
        self.repository = repository

    async def set_command_count(self, count: int) -> None:
        """Set command count.
        Args:
            count (int): Command count.
        """
        await self.repository.set_command_count(count)

    async def set_cog_count(self, count: int) -> None:
        """Set cog count.
        Args:
            count (int): Cog count.
        """
        await self.repository.set_cog_count(count)

    async def set_guild_count(self, count: int) -> None:
        """Set guild count.
        Args:
            count (int): Guild count.
        """
        await self.repository.set_guild_count(count)

    async def set_user_count(self, count: int) -> None:
        """Set user count.
        Args:
            count (int): User count.
        """
        await self.repository.set_user_count(count)

    async def set_commands(self, commands: dict[str, Any]) -> None:
        """Set commands.
        Args:
            commands (dict): Commands.
        """
        await self.repository.set_commands(commands)

    async def set_bot_version(self, version: str) -> None:
        """Set bot version.
        Args:
            version (str): Bot version.
        """
        await self.repository.set_bot_version(version)
