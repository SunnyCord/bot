###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user import DatabaseUser
from repository.user import UserRepository


class UserService:
    """Service for user data."""

    __slots__ = ("repository",)

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_one(self, user_id: int) -> DatabaseUser:
        """Get user data from database.
        Args:
            user_id (int): User ID.
        Raises:
            ValueError: User not found.
        Returns:
            DatabaseUser: User data.
        """
        return await self.repository.get_one(user_id)

    async def get_many(self) -> list[DatabaseUser]:
        """Get all users from database.
        Returns:
            list[DatabaseUser]: List of users.
        """
        return await self.repository.get_many()

    async def add(self, user: DatabaseUser) -> None:
        """Add new user to database.
        Args:
            user (DatabaseUser): User data.
        """
        await self.repository.add(user)

    async def update(self, user: DatabaseUser) -> None:
        """Update user data.
        Args:
            user (DatabaseUser): User data.
        """
        await self.repository.update(user)

    async def delete(self, user_id: int) -> None:
        """Delete user data.
        Args:
            user_id (int): User ID.
        """
        await self.repository.delete(user_id)

    async def blacklist(self, user_id: int) -> None:
        """Blacklist user.
        Args:
            user_id (int): User ID.
        """
        try:
            user = await self.get_one(user_id)
            user.blacklist = True
            await self.update(user)
        except ValueError:
            user = DatabaseUser(discord_id=user_id, blacklist=True)
            await self.add(user)

    async def unblacklist(self, user_id: int) -> None:
        """Unblacklist user.
        Args:
            user_id (int): User ID.
        """
        try:
            user = await self.get_one(user_id)
            user.blacklist = False
            await self.update(user)
        except ValueError:
            pass

    async def is_blacklisted(self, user_id: int) -> bool:
        """Check if user is blacklisted.
        Args:
            user_id (int): User ID.
        Returns:
            bool: True if user is blacklisted.
        """
        try:
            user = await self.get_one(user_id)
            return user.blacklist
        except ValueError:
            return False
