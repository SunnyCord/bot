###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class GuildSettingsRepository:
    """Guild Settings Repository"""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, guild_id: int) -> dict[str, Any] | None:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Returns:
            Optional[dict[str, Any]]: Guild settings data.
        """
        return await self.database.guild_settings.find_one({"guild_id": guild_id})

    async def get_many(
        self,
        booster_id: int | None = None,
        boosted: bool = False,
    ) -> list[dict[str, Any]]:
        """Get all guild settings from database.

        Returns:
            list[dict[str, Any]]: List of guild settings data.
        """
        query = {}
        if booster_id is not None:
            query["booster"] = booster_id
        elif boosted:
            query["booster"] = {"$ne": None}

        return await self.database.guild_settings.find(query).to_list(None)

    async def count(self, booster_id: int | None) -> int:
        """Get guild settings count.

        Returns:
            int: Guild settings count.
        """
        query = {}
        if booster_id is not None:
            query["booster"] = booster_id

        return await self.database.guild_settings.count_documents(query)

    async def add(self, guild_settings: dict[str, Any]) -> None:
        """Add new guild settings to database.

        Args:
            guild_settings (dict[str, Any]): Guild settings data.
        """
        await self.database.guild_settings.insert_one(guild_settings)

    async def update(self, guild_id: int, guild_settings: dict[str, Any]) -> None:
        """Update guild settings.

        Args:
            guild_id (int): Guild ID.
            guild_settings (dict[str, Any]): Guild settings data.
        """
        await self.database.guild_settings.update_one(
            {"guild_id": guild_id},
            {"$set": guild_settings},
            upsert=True,
        )

    async def delete(self, guild_id: int) -> None:
        """Delete guild settings.

        Args:
            guild_id (int): Guild ID.
        """
        await self.database.guild_settings.delete_one({"guild_id": guild_id})
