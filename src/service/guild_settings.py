###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.guild_settings import GuildSettings
from repository.guild_settings import GuildSettingsRepository


class GuildSettingsService:
    """Guild Settings Service"""

    def __init__(self, repository: GuildSettingsRepository) -> None:
        self.repository = repository

    async def get_one(self, guild_id: int) -> GuildSettings:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Raises:
            ValueError: Settings not found.

        Returns:
            GuildSettings: Guild settings.
        """
        return await self.repository.get_one(guild_id)

    async def get_many(self) -> list[GuildSettings]:
        """Get all guild settings from database.

        Returns:
            list[GuildSettings]: List of guild settings.
        """
        return await self.repository.get_many()

    async def add(self, guild_settings: GuildSettings) -> None:
        """Add new guild settings to database.

        Args:
            guild_settings (GuildSettings): Guild settings.
        """
        await self.repository.add(guild_settings)

    async def update(self, guild_settings: GuildSettings) -> None:
        """Update guild settings.

        Args:
            guild_settings (GuildSettings): Guild settings.
        """
        await self.repository.update(guild_settings)

    async def delete(self, guild_id: int) -> None:
        """Delete guild settings.

        Args:
            guild_id (int): Guild ID.
        """
        await self.repository.delete(guild_id)

    async def create(self, guild_id: int) -> GuildSettings:
        """Create default settings for guild.

        Args:
            guild_id (int): Guild ID.

        Returns:
            GuildSettings: Guild settings.
        """
        settings = GuildSettings(guild_id=guild_id)
        await self.add(settings)
        return settings

    async def get_prefix(self, guild_id: int) -> str:
        """Get guild prefix.

        Args:
            guild_id (int): Guild ID.

        Returns:
            str: Guild prefix.
        """
        try:
            settings = await self.get_one(guild_id)
            return settings.prefix
        except ValueError:
            return ""

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        """Set guild prefix.

        Args:
            guild_id (int): Guild ID.
            prefix (str): Guild prefix.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            settings = await self.create(guild_id)

        settings.prefix = prefix
        await self.update(settings)

    async def clear_prefix(self, guild_id: int) -> None:
        """Clear guild prefix.

        Args:
            guild_id (int): Guild ID.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            return

        settings.prefix = ""
        await self.update(settings)
