###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from redis.asyncio import Redis


class BeatmapRepository:
    """Repository for cached beatmap data."""

    __slots__ = ("redis",)

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_one(self, channel_id: int) -> str | None:
        """Get beatmap from database.

        Args:
            channel_id (int): Channel ID.
        Returns:
            Optional[str]: Beatmap data.
        """
        return await self.redis.get(f"sunny:{channel_id}:beatmap")

    async def get_many(self) -> list[str]:
        """Get all beatmaps from database.

        Returns:
            list[Any]: List of beatmap data.
        """
        return await self.redis.keys("sunny:*:beatmap")

    async def add(self, channel_id: int, beatmap: str) -> None:
        """Add new beatmap to database.

        Args:
            channel_id (int): Channel ID.
            beatmap (str): Beatmap JSON data.
        """
        await self.redis.set(
            f"sunny:{channel_id}:beatmap",
            beatmap,
        )

    async def update(self, channel_id: int, beatmap: str) -> None:
        """Update beatmap data.

        Args:
            channel_id (int): Channel ID.
            beatmap (str): Beatmap JSON data.
        """
        await self.redis.set(
            f"sunny:{channel_id}:beatmap",
            beatmap,
        )

    async def delete(self, channel_id: int) -> None:
        """Delete beatmap data.

        Args:
            channel_id (int): Channel ID.
        """
        await self.redis.delete(f"sunny:{channel_id}:beatmap")
