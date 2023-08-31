###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class UserPreferencesRepository:
    """User Preferences Repository"""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, discord_id: int) -> dict[str, Any] | None:
        """Get user preferences from database.

        Args:
            discord_id (int): Discord ID.

        Returns:
            Optional[dict[str, Any]]: User preferences data.
        """
        return await self.database.user_preferences.find_one(
            {"discord_id": discord_id},
        )

    async def get_many(self) -> list[dict[str, Any]]:
        """Get all user preferences from database.

        Returns:
            list[dict[str, Any]]: List of user preferences data.
        """
        return await self.database.user_preferences.find().to_list(None)

    async def add(self, user_preferences: dict[str, Any]) -> None:
        """Add new user preferences to database.

        Args:
            user_preferences (dict[str, Any]): User preferences data.
        """
        await self.database.user_preferences.insert_one(user_preferences)

    async def update(self, discord_id: int, user_preferences: dict[str, Any]) -> None:
        """Update user preferences.

        Args:
            discord_id (int): Discord ID.
            user_preferences (dict[str, Any]): User preferences data.
        """
        await self.database.user_preferences.update_one(
            {"discord_id": discord_id},
            {"$set": user_preferences},
            upsert=True,
        )

    async def delete(self, discord_id: int) -> None:
        """Delete user preferences from database.

        Args:
            discord_id (int): Discord ID.
        """
        await self.database.user_preferences.delete_one({"discord_id": discord_id})
