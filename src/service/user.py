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
        data = await self.repository.get_one(user_id)
        if data is None:
            raise ValueError("User not found.")
        return DatabaseUser.model_validate(data)

    async def get_safe(self, user_id: int) -> DatabaseUser:
        """Get user data from database.
        Args:
            user_id (int): User ID.
        Returns:
            DatabaseUser: User data.
        """
        try:
            return await self.get_one(user_id)
        except ValueError:
            return DatabaseUser(discord_id=user_id)

    async def get_many(self) -> list[DatabaseUser]:
        """Get all users from database.
        Returns:
            list[DatabaseUser]: List of users.
        """
        data = await self.repository.get_many()
        return [DatabaseUser.model_validate(user) for user in data]

    async def add(self, user: DatabaseUser) -> None:
        """Add new user to database.
        Args:
            user (DatabaseUser): User data.
        """
        await self.repository.add(user.model_dump())

    async def update(self, user: DatabaseUser) -> None:
        """Update user data.
        Args:
            user (DatabaseUser): User data.
        """
        await self.repository.update(
            user.discord_id,
            user.model_dump(exclude={"discord_id"}),
        )

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
        user = await self.get_safe(user_id)
        user.blacklist = True
        await self.update(user)

    async def unblacklist(self, user_id: int) -> None:
        """Unblacklist user.
        Args:
            user_id (int): User ID.
        """
        user = await self.get_safe(user_id)
        user.blacklist = False
        await self.update(user)

    async def is_blacklisted(self, user_id: int) -> bool:
        """Check if user is blacklisted.
        Args:
            user_id (int): User ID.
        Returns:
            bool: True if user is blacklisted.
        """
        user = await self.get_safe(user_id)
        return user.blacklist
