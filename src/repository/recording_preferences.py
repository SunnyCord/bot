###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user_preferences import RecordingPreferences
from motor.motor_asyncio import AsyncIOMotorDatabase


class RecordingPreferencesRepository:
    """Recording Preferences Repository"""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, discord_id: int) -> RecordingPreferences:
        """Get recording preferences from database.

        Args:
            discord_id (int): Discord ID.

        Raises:
            ValueError: Preferences not found.

        Returns:
            RecordingPreferences: Recording preferences.
        """
        preferences = await self.database.recording_preferences.find_one(
            {"discord_id": discord_id},
        )
        if preferences is None:
            raise ValueError("Preferences not found.")
        return RecordingPreferences.model_validate(preferences)

    async def get_many(self) -> list[RecordingPreferences]:
        """Get all recording preferences from database.

        Returns:
            list[RecordingPreferences]: List of recording preferences.
        """
        preferences = await self.database.recording_preferences.find().to_list(None)
        return [
            RecordingPreferences.model_validate(preference)
            for preference in preferences
        ]

    async def add(self, recording_preferences: RecordingPreferences) -> None:
        """Add new recording preferences to database.

        Args:
            discord_id (int): Discord ID.
            recording_preferences (RecordingPreferences): Recording preferences.
        """
        await self.database.recording_preferences.insert_one(
            recording_preferences.dict(exclude_defaults=True),
        )

    async def update(self, preferences: RecordingPreferences) -> None:
        """Update recording preferences.

        Args:
            discord_id (int): Discord ID.
            preferences (RecordingPreferences): Recording preferences.
        """
        await self.database.recording_preferences.update_one(
            {"discord_id": preferences.discord_id},
            {
                "$set": preferences.dict(
                    exclude={"discord_id"},
                    exclude_unset=True,
                ),
            },
        )

    async def delete(self, discord_id: int) -> None:
        """Delete recording preferences from database.

        Args:
            discord_id (int): Discord ID.
        """
        await self.database.recording_preferences.delete_one(
            {"discord_id": discord_id},
        )
