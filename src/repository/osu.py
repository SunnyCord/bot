###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import OAuthToken
from aiosu.v2.repository import BaseTokenRepository
from models.user import TokenDTO
from motor.motor_asyncio import AsyncIOMotorDatabase


class OsuRepository(BaseTokenRepository):
    """Repository for osu! tokens."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def exists(self, discord_id: int) -> bool:
        """Check if token exists in database.

        Args:
            discord_id (int): Discord ID.
        Returns:
            bool: True if token exists, False otherwise.
        """
        return (
            await self.database.tokens.count_documents({"discord_id": discord_id}) > 0
        )

    async def get(self, discord_id: int) -> OAuthToken:
        """Get osu! token from database.

        Args:
            discord_id (int): Discord ID.
        Raises:
            ValueError: Token not found.
        Returns:
            OAuthToken: osu! token.
        """
        token = await self.database.tokens.find_one({"discord_id": discord_id})
        if token is None:
            raise ValueError("Token not found.")
        return OAuthToken(**token["token"])

    async def add(self, discord_id: int, token: OAuthToken) -> None:
        """Add new token to database.

        Args:
            discord_id (int): Discord ID.
            token (OAuthToken): osu! token.
        """
        token_dto = TokenDTO(discord_id=discord_id, token=token)
        await self.database.tokens.insert_one(token_dto.dict())

    async def update(self, session_id: int, token: OAuthToken) -> None:
        """Update token in database.

        Args:
            session_id (int): Session ID.
            token (OAuthToken): osu! token.
        """
        await self.database.tokens.update_one(
            {"discord_id": session_id},
            {"$set": {"token": token.dict()}},
        )

    async def delete(self, discord_id: int) -> None:
        """Delete token data.

        Args:
            discord_id (int): Discord ID.
        """
        await self.database.tokens.delete_one({"discord_id": discord_id})
