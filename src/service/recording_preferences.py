###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from models.user_preferences import RecordingPreferences
from repository import RecordingPreferencesRepository


class RecordingPreferencesService:
    """Recording Preferences Service"""

    __slots__ = ("repository",)

    def __init__(self, repository: RecordingPreferencesRepository) -> None:
        self.repository = repository

    async def get_one(self, discord_id: int) -> RecordingPreferences:
        """Get recording preferences from database.

        Args:
            discord_id (int): Discord ID.

        Raises:
            ValueError: Preferences not found.

        Returns:
            RecordingPreferences: Recording preferences.
        """
        return await self.repository.get_one(discord_id)

    async def get_many(self) -> list[RecordingPreferences]:
        """Get all recording preferences from database.

        Returns:
            list[RecordingPreferences]: List of recording preferences.
        """
        return await self.repository.get_many()

    async def get_safe(self, discord_id: int) -> RecordingPreferences:
        """Get recording preferences from database.

        Args:
            discord_id (int): Discord ID.

        Returns:
            RecordingPreferences: Recording preferences.
        """
        try:
            return await self.repository.get_one(discord_id)
        except ValueError:
            return RecordingPreferences(discord_id=discord_id)

    async def add(self, recording_preferences: RecordingPreferences) -> None:
        """Add new recording preferences to database.

        Args:
            recording_preferences (RecordingPreferences): Recording preferences.
        """
        await self.repository.add(recording_preferences)

    async def update(self, preferences: RecordingPreferences) -> None:
        """Update recording preferences.

        Args:
            preferences (RecordingPreferences): Recording preferences.
        """
        await self.repository.update(preferences)

    async def delete(self, discord_id: int) -> None:
        """Delete recording preferences.

        Args:
            discord_id (int): Discord ID.
        """
        await self.repository.delete(discord_id)

    async def toggle_option(self, discord_id: int, option: str) -> bool:
        """Toggle recording preferences option.

        Args:
            discord_id (int): Discord ID.
            option (str): Option to toggle.

        Returns:
            bool: New value of option.
        """
        try:
            preferences = await self.get_one(discord_id)
        except ValueError:
            preferences = RecordingPreferences(discord_id=discord_id)
            await self.add(preferences)
        value = getattr(preferences, option)
        setattr(preferences, option, not value)
        await self.update(preferences)
        return not value

    async def set_option(self, discord_id: int, option: str, value: Any) -> None:
        """Set recording preferences option.

        Args:
            discord_id (int): Discord ID.
            option (str): Option to toggle.
            value (Any): Value to set.
        """
        try:
            preferences = await self.get_one(discord_id)
        except ValueError:
            preferences = RecordingPreferences(discord_id=discord_id)
            await self.add(preferences)
        setattr(preferences, option, value)
        await self.update(preferences)
