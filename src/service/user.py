###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.user import User
from repository.user import UserRepository


class UserService:
    """Service for user data."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_one(self, user_id: int) -> User:
        """Get user data from database.
        Args:
            user_id (int): User ID.
        Raises:
            ValueError: User not found.
        Returns:
            User: User data.
        """
        return await self.repository.get_one(user_id)

    async def get_many(self) -> list[User]:
        """Get all users from database.
        Returns:
            list[User]: List of users.
        """
        return await self.repository.get_many()

    async def add(self, user: User) -> None:
        """Add new user to database.
        Args:
            user (User): User data.
        """
        await self.repository.add(user)

    async def update(self, user: User) -> None:
        """Update user data.
        Args:
            user (User): User data.
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
            user = User(discord_id=user_id, blacklist=True)
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
