###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    """Repository for user data."""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def get_one(self, discord_id: int) -> dict[str, Any] | None:
        """Get user data from database.

        Args:
            discord_id (int): User ID.
        Returns:
            Optional[dict[str, Any]]: User data.
        """
        return await self.database.users.find_one({"discord_id": discord_id})

    async def get_many(self) -> list[dict[str, Any]]:
        """Get all users from database.

        Returns:
            list[dict[str, Any]]: List of users.
        """
        return await self.database.users.find().to_list(None)

    async def add(self, user: dict[str, Any]) -> None:
        """Add new user to database.

        Args:
            user (dict[str, Any]): User data.
        """
        await self.database.users.insert_one(user)

    async def update(self, discord_id: int, user: dict[str, Any]) -> None:
        """Update user data.

        Args:
            discord_id (int): User Discord ID.
            user (dict[str, Any]): User data.
        """
        await self.database.users.update_one(
            {"discord_id": discord_id},
            {"$set": user},
            upsert=True,
        )

    async def delete(self, discord_id: int) -> None:
        """Delete user data.

        Args:
            discord_id (int): User Discord ID.
        """
        await self.database.users.delete_one({"discord_id": discord_id})
