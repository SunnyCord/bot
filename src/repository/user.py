###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user import DatabaseUser
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    """Repository for user data."""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def get_one(self, discord_id: int) -> DatabaseUser:
        """Get user data from database.

        Args:
            discord_id (int): User ID.
        Raises:
            ValueError: User not found.
        Returns:
            DatabaseUser: User data.
        """
        user = await self.database.users.find_one({"discord_id": discord_id})
        if user is None:
            raise ValueError("User not found.")
        return DatabaseUser.model_validate(user)

    async def get_many(self) -> list[DatabaseUser]:
        """Get all users from database.

        Returns:
            list[DatabaseUser]: List of users.
        """
        users = await self.database.users.find().to_list(None)
        return [DatabaseUser.model_validate(user) for user in users]

    async def add(self, user: DatabaseUser) -> None:
        """Add new user to database.

        Args:
            user (DatabaseUser): User data.
        """
        await self.database.users.insert_one(user.dict())

    async def update(self, user: DatabaseUser) -> None:
        """Update user data.

        Args:
            user (DatabaseUser): User data.
        """
        await self.database.users.update_one(
            {"discord_id": user.discord_id},
            {"$set": user.dict()},
            upsert=True,
        )

    async def delete(self, discord_id: int) -> None:
        """Delete user data.

        Args:
            discord_id (int): User Discord ID.
        """
        await self.database.users.delete_one({"discord_id": discord_id})
