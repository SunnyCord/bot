###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user_preferences import UserPreferences
from models.weather import Units
from repository.user_preferences import UserPreferencesRepository


class UserPreferencesService:
    """User Preferences Service"""

    __slots__ = ("repository",)

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
        data = await self.repository.get_one(discord_id)
        if data is None:
            raise ValueError("Preferences not found.")
        return UserPreferences.model_validate(data)

    async def get_safe(self, discord_id: int) -> UserPreferences:
        """Get user preferences from database.

        Args:
            discord_id (int): Discord ID.

        Returns:
            UserPreferences: User preferences.
        """
        try:
            return await self.get_one(discord_id)
        except ValueError:
            return UserPreferences(discord_id=discord_id)

    async def get_many(self) -> list[UserPreferences]:
        """Get all user preferences from database.

        Returns:
            list[UserPreferences]: List of user preferences.
        """
        data = await self.repository.get_many()
        return [
            UserPreferences.model_validate(user_preference) for user_preference in data
        ]

    async def add(self, user_preferences: UserPreferences) -> None:
        """Add new user preferences to database.

        Args:
            user_preferences (UserPreferences): User preferences.
        """
        await self.repository.add(user_preferences.model_dump())

    async def create(self, discord_id: int) -> UserPreferences:
        """Create user preferences.

        Args:
            discord_id (int): Discord ID.

        Returns:
            UserPreferences: User preferences.
        """
        user_preferences = await self.get_safe(discord_id)
        await self.update(user_preferences)
        return user_preferences

    async def update(self, user_preferences: UserPreferences) -> None:
        """Update user preferences.

        Args:
            user_preferences (UserPreferences): User preferences.
        """
        await self.repository.update(
            user_preferences.discord_id,
            user_preferences.model_dump(exclude={"discord_id"}),
        )

    async def delete(self, discord_id: int) -> None:
        """Delete user preferences.

        Args:
            discord_id (int): Discord ID.
        """
        await self.repository.delete(discord_id)

    async def get_lazer(self, discord_id: int) -> bool:
        """Get user lazer preference.

        Args:
            discord_id (int): Discord ID.

        Returns:
            bool: Lazer preference.
        """
        user_preferences = await self.get_safe(discord_id)
        return user_preferences.lazer

    async def toggle_lazer(self, discord_id: int) -> bool:
        """Toggle user lazer preference.

        Args:
            discord_id (int): Discord ID.

        Returns:
            bool: Lazer preference.
        """
        user_preferences = await self.get_safe(discord_id)
        user_preferences.lazer = not user_preferences.lazer
        await self.update(user_preferences)
        return user_preferences.lazer

    async def get_units(self, discord_id: int) -> Units:
        """Get user units preference.

        Args:
            discord_id (int): Discord ID.

        Returns:
            Units: Units preference.
        """
        user_preferences = await self.get_safe(discord_id)
        return user_preferences.units

    async def set_units(self, discord_id: int, units: Units) -> None:
        """Set user units preference.

        Args:
            discord_id (int): Discord ID.
            units (Units): Units preference.
        """
        user_preferences = await self.get_safe(discord_id)
        user_preferences.units = units
        await self.update(user_preferences)
