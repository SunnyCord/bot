from __future__ import annotations

from models.settings import GuildSetting
from motor.motor_asyncio import AsyncIOMotorDatabase


class SettingsRepository:
    """Settings Repository"""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, guild_id: int) -> GuildSetting:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Raises:
            ValueError: Settings not found.

        Returns:
            GuildSetting: Guild settings.
        """
        settings = await self.database.settings.find_one({"guild_id": guild_id})
        if settings is None:
            raise ValueError("Settings not found.")
        return GuildSetting(**settings)

    async def get_many(self) -> list[GuildSetting]:
        """Get all guild settings from database.

        Returns:
            list[GuildSetting]: List of guild settings.
        """
        settings = await self.database.settings.find().to_list(None)
        return [GuildSetting(**setting) for setting in settings]

    async def add(self, settings: GuildSetting) -> None:
        """Add new guild settings to database.

        Args:
            settings (GuildSetting): Guild settings.
        """
        await self.database.settings.insert_one(**settings.dict())

    async def update(self, settings: GuildSetting) -> None:
        """Update guild settings.

        Args:
            settings (GuildSetting): Guild settings.
        """
        await self.database.settings.update_one(
            {"guild_id": settings.guild_id},
            {"$set": settings.dict(exclude={"guild_id"})},
            upsert=True,
        )

    async def delete(self, guild_id: int) -> None:
        """Delete guild settings.

        Args:
            guild_id (int): Guild ID.
        """
        await self.database.settings.delete_one({"guild_id": guild_id})
