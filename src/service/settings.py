from __future__ import annotations

from models.settings import GuildSetting
from repository.settings import SettingsRepository


class SettingsService:
    """Settings Service"""

    def __init__(self, settings_repository: SettingsRepository) -> None:
        self.settings_repository = settings_repository

    async def get_one(self, guild_id: int) -> GuildSetting:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Raises:
            ValueError: Settings not found.

        Returns:
            GuildSetting: Guild settings.
        """
        return await self.settings_repository.get_one(guild_id)

    async def get_many(self) -> list[GuildSetting]:
        """Get all guild settings from database.

        Returns:
            list[GuildSetting]: List of guild settings.
        """
        return await self.settings_repository.get_many()

    async def add(self, settings: GuildSetting) -> None:
        """Add new guild settings to database.

        Args:
            settings (GuildSetting): Guild settings.
        """
        await self.settings_repository.add(settings)

    async def update(self, settings: GuildSetting) -> None:
        """Update guild settings.

        Args:
            settings (GuildSetting): Guild settings.
        """
        await self.settings_repository.update(settings)

    async def delete(self, guild_id: int) -> None:
        """Delete guild settings.

        Args:
            guild_id (int): Guild ID.
        """
        await self.settings_repository.delete(guild_id)

    async def create(self, guild_id: int) -> None:
        """Create default settings for guild.

        Args:
            guild_id (int): Guild ID.
        """
        settings = GuildSetting(guild_id=guild_id)
        await self.add(settings)
