from __future__ import annotations

from aiosu.models import OAuthToken
from models.user import TokenDTO
from repository.osu import OsuRepository


class OsuService:
    """Service for osu! data."""

    def __init__(self, token_repository: OsuRepository):
        self.user_repository = token_repository

    async def get_one(self, discord_id: int) -> OAuthToken:
        """Get osu! token from database.
        Args:
            discord_id (int): Discord ID.
        Raises:
            ValueError: Token not found.
        Returns:
            OAuthToken: osu! token.
        """
        return await self.user_repository.get_one(discord_id)

    async def get_many(self) -> list[OAuthToken]:
        """Get all tokens from database.
        Returns:
            list[OAuthToken]: List of tokens.
        """
        return await self.user_repository.get_many()

    async def add(self, token: TokenDTO) -> None:
        """Add new token to database.
        Args:
            discord_id (int): Discord ID.
            token (OAuthToken): osu! token.
        """
        await self.user_repository.add(token)

    async def update(self, token: TokenDTO) -> None:
        """Update token data.
        Args:
            discord_id (int): Discord ID.
            token (OAuthToken): osu! token.
        """
        await self.user_repository.update(token)

    async def delete(self, discord_id: int) -> None:
        """Delete token from database.
        Args:
            discord_id (int): Discord ID.
        """
        await self.user_repository.delete(discord_id)
