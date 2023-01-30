from __future__ import annotations

from typing import Any

from repository import StatsRepository


class StatsService:
    """Service for statistics."""

    def __init__(self, stats_repository: StatsRepository) -> None:
        self.stats_repository = stats_repository

    async def set_command_count(self, count: int) -> None:
        """Set command count.
        Args:
            count (int): Command count.
        """
        await self.stats_repository.set_command_count(count)

    async def set_cog_count(self, count: int) -> None:
        """Set cog count.
        Args:
            count (int): Cog count.
        """
        await self.stats_repository.set_cog_count(count)

    async def set_guild_count(self, count: int) -> None:
        """Set guild count.
        Args:
            count (int): Guild count.
        """
        await self.stats_repository.set_guild_count(count)

    async def set_commands(self, commands: dict[str, Any]) -> None:
        """Set commands.
        Args:
            commands (dict): Commands.
        """
        await self.stats_repository.set_commands(commands)
