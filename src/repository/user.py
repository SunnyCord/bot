###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user import User
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    """Repository for user data."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def get_one(self, discord_id: int) -> User:
        """Get user data from database.

        Args:
            discord_id (int): User ID.
        Raises:
            ValueError: User not found.
        Returns:
            User: User data.
        """
        user = await self.database.users.find_one({"discord_id": discord_id})
        if user is None:
            raise ValueError("User not found.")
        return User(**user)

    async def get_many(self) -> list[User]:
        """Get all users from database.

        Returns:
            list[User]: List of users.
        """
        users = await self.database.users.find().to_list(None)
        return [User(**user) for user in users]

    async def add(self, user: User) -> None:
        """Add new user to database.

        Args:
            user (User): User data.
        """
        await self.database.users.insert_one(user.dict())

    async def update(self, user: User) -> None:
        """Update user data.

        Args:
            user (User): User data.
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
