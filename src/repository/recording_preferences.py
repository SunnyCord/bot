###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class RecordingPreferencesRepository:
    """Recording Preferences Repository"""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def get_one(self, discord_id: int) -> dict[str, Any] | None:
        """Get recording preferences from database.

        Args:
            discord_id (int): Discord ID.
        Returns:
            Optional[dict[str, Any]]: Recording preferences data.
        """
        return await self.database.recording_preferences.find_one(
            {"discord_id": discord_id},
        )

    async def get_many(self) -> list[dict[str, Any]]:
        """Get all recording preferences from database.

        Returns:
            list[dict[str, Any]]: List of recording preferences.
        """
        return await self.database.recording_preferences.find().to_list(None)

    async def add(self, recording_preferences: dict[str, Any]) -> None:
        """Add new recording preferences to database.

        Args:
            discord_id (int): Discord ID.
            recording_preferences (dict[str, Any]): Recording preferences.
        """
        await self.database.recording_preferences.insert_one(recording_preferences)

    async def update(
        self,
        discord_id: int,
        recording_preferences: dict[str, Any],
    ) -> None:
        """Update recording preferences.

        Args:
            discord_id (int): Discord ID.
            recording_preferences (dict[str, Any]): Recording preferences.
        """
        await self.database.recording_preferences.update_one(
            {"discord_id": discord_id},
            {
                "$set": recording_preferences,
            },
            upsert=True,
        )

    async def delete(self, discord_id: int) -> None:
        """Delete recording preferences from database.

        Args:
            discord_id (int): Discord ID.
        """
        await self.database.recording_preferences.delete_one(
            {"discord_id": discord_id},
        )
