###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.guild_settings import GuildSettings
from motor.motor_asyncio import AsyncIOMotorDatabase


class GuildSettingsRepository:
    """Guild Settings Repository"""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, guild_id: int) -> GuildSettings:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Raises:
            ValueError: Settings not found.

        Returns:
            GuildSettings: Guild settings.
        """
        guild_settings = await self.database.guild_settings.find_one(
            {"guild_id": guild_id},
        )
        if guild_settings is None:
            raise ValueError("Settings not found.")
        return GuildSettings(**guild_settings)

    async def get_many(self) -> list[GuildSettings]:
        """Get all guild settings from database.

        Returns:
            list[GuildSettings]: List of guild settings.
        """
        guild_settings = await self.database.guild_settings.find().to_list(None)
        return [GuildSettings(**guild_setting) for guild_setting in guild_settings]

    async def add(self, guild_settings: GuildSettings) -> None:
        """Add new guild settings to database.

        Args:
            settings (GuildSettings): Guild settings.
        """
        await self.database.guild_settings.insert_one(guild_settings.dict())

    async def update(self, guild_settings: GuildSettings) -> None:
        """Update guild settings.

        Args:
            settings (GuildSettings): Guild settings.
        """
        await self.database.guild_settings.update_one(
            {"guild_id": guild_settings.guild_id},
            {"$set": guild_settings.dict(exclude={"guild_id"})},
            upsert=True,
        )

    async def delete(self, guild_id: int) -> None:
        """Delete guild settings.

        Args:
            guild_id (int): Guild ID.
        """
        await self.database.guild_settings.delete_one({"guild_id": guild_id})