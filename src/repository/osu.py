from __future__ import annotations

from aiosu.models import OAuthToken
from models.user import TokenDTO
from motor.motor_asyncio import AsyncIOMotorDatabase


class OsuRepository:
    """Repository for osu! tokens."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def get_one(self, discord_id: int) -> OAuthToken:
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

    async def get_many(self) -> list[OAuthToken]:
        """Get all tokens from database.

        Returns:
            list[OAuthToken]: List of tokens.
        """
        tokens = await self.database.tokens.find().to_list(None)
        return [OAuthToken(**token["token"]) for token in tokens]

    async def add(self, token: TokenDTO) -> None:
        """Add new token to database.

        Args:
            discord_id (int): Discord ID.
            token (OAuthToken): osu! token.
        """
        await self.database.tokens.insert_one(**token.dict())

    async def update(self, token: TokenDTO) -> None:
        """Update token data.

        Args:
            discord_id (int): Discord ID.
            token (OAuthToken): osu! token.
        """
        await self.database.tokens.update_one(
            {"discord_id": token.discord_id},
            {"$set": token.dict(exclude={"discord_id"})},
            upsert=True,
        )

    async def delete(self, discord_id: int) -> None:
        """Delete token data.

        Args:
            discord_id (int): Discord ID.
        """
        await self.database.tokens.delete_one({"discord_id": discord_id})
