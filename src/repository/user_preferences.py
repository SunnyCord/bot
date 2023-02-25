###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user_preferences import UserPreferences
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserPreferencesRepository:
    """User Preferences Repository"""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, discord_id: int) -> UserPreferences:
        """Get user preferences from database.

        Args:
            discord_id (int): Discord ID.

        Raises:
            ValueError: Preferences not found.

        Returns:
            UserPreferences: User preferences.
        """
        user_preferences = await self.database.user_preferences.find_one(
            {"discord_id": discord_id},
        )
        if user_preferences is None:
            raise ValueError("Preferences not found.")
        return UserPreferences(**user_preferences)

    async def get_many(self) -> list[UserPreferences]:
        """Get all user preferences from database.

        Returns:
            list[UserPreferences]: List of user preferences.
        """
        user_preferences = await self.database.user_preferences.find().to_list(None)
        return [
            UserPreferences(**user_preference) for user_preference in user_preferences
        ]

    async def add(self, user_preferences: UserPreferences) -> None:
        """Add new user preferences to database.

        Args:
            user_preferences (UserPreferences): User preferences.
        """
        await self.database.user_preferences.insert_one(user_preferences.dict())

    async def update(self, user_preferences: UserPreferences) -> None:
        """Update user preferences.

        Args:
            user_preferences (UserPreferences): User preferences.
        """
        await self.database.user_preferences.update_one(
            {"discord_id": user_preferences.discord_id},
            {"$set": user_preferences.dict(exclude={"discord_id"})},
        )

    async def delete(self, discord_id: int) -> None:
        """Delete user preferences from database.

        Args:
            discord_id (int): Discord ID.
        """
        await self.database.user_preferences.delete_one({"discord_id": discord_id})
