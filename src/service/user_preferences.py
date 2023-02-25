###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user_preferences import UserPreferences
from repository.user_preferences import UserPreferencesRepository


class UserPreferencesService:
    """User Preferences Service"""

    def __init__(self, repository: UserPreferencesRepository) -> None:
        self.repository = repository

    async def get_one(self, discord_id: int) -> UserPreferences:
        """Get user preferences from database.

        Args:
            discord_id (int): Discord ID.

        Raises:
            ValueError: Preferences not found.

        Returns:
            UserPreferences: User preferences.
        """
        return await self.repository.get_one(discord_id)

    async def get_many(self) -> list[UserPreferences]:
        """Get all user preferences from database.

        Returns:
            list[UserPreferences]: List of user preferences.
        """
        return await self.repository.get_many()

    async def add(self, user_preferences: UserPreferences) -> None:
        """Add new user preferences to database.

        Args:
            user_preferences (UserPreferences): User preferences.
        """
        await self.repository.add(user_preferences)

    async def update(self, user_preferences: UserPreferences) -> None:
        """Update user preferences.

        Args:
            user_preferences (UserPreferences): User preferences.
        """
        await self.repository.update(user_preferences)

    async def delete(self, discord_id: int) -> None:
        """Delete user preferences.

        Args:
            discord_id (int): Discord ID.
        """
        await self.repository.delete(discord_id)

    async def create(self, discord_id: int) -> UserPreferences:
        """Create user preferences.

        Args:
            discord_id (int): Discord ID.

        Returns:
            UserPreferences: User preferences.
        """
        preferences = UserPreferences(discord_id=discord_id)
        await self.add(preferences)
        return preferences

    async def get_lazer(self, discord_id: int) -> bool:
        """Get user lazer preference.

        Args:
            discord_id (int): Discord ID.

        Returns:
            bool: Lazer preference.
        """
        try:
            user_preferences = await self.get_one(discord_id)
            return user_preferences.lazer
        except ValueError:
            return False

    async def toggle_lazer(self, discord_id: int) -> bool:
        """Toggle user lazer preference.

        Args:
            discord_id (int): Discord ID.

        Returns:
            bool: Lazer preference.
        """
        try:
            user_preferences = await self.get_one(discord_id)
        except ValueError:
            user_preferences = await self.create(discord_id)

        user_preferences.lazer = not user_preferences.lazer
        await self.update(user_preferences)
        return user_preferences.lazer
