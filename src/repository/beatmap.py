###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import Beatmap
from redis.asyncio import Redis


class BeatmapRepository:
    """Repository for cached beatmap data."""

    __slots__ = ("redis",)

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_one(self, channel_id: int) -> Beatmap:
        """Get beatmap from database.

        Args:
            channel_id (int): Channel ID.
        Raises:
            ValueError: Beatmap not found.
        Returns:
            Beatmap: Beatmap data.
        """
        beatmap = await self.redis.get(f"sunny:{channel_id}:beatmap")
        if beatmap is None:
            raise ValueError("Beatmap not found.")
        return Beatmap.model_validate_json(beatmap)

    async def get_many(self) -> list[Beatmap]:
        """Get all beatmaps from database.

        Returns:
            list[Beatmap]: List of beatmaps.
        """
        beatmaps = await self.redis.keys("sunny:*:beatmap")
        return [Beatmap.model_validate_json(beatmap) for beatmap in beatmaps]

    async def add(self, channel_id: int, beatmap: Beatmap) -> None:
        """Add new beatmap to database.

        Args:
            channel_id (int): Channel ID.
            beatmap (Beatmap): Beatmap data.
        """
        await self.redis.set(
            f"sunny:{channel_id}:beatmap",
            beatmap.model_dump_json(),
        )

    async def update(self, channel_id: int, beatmap: Beatmap) -> None:
        """Update beatmap data.

        Args:
            channel_id (int): Channel ID.
            beatmap (Beatmap): Beatmap data.
        """
        await self.redis.set(
            f"sunny:{channel_id}:beatmap",
            beatmap.model_dump_json(),
        )

    async def delete(self, channel_id: int) -> None:
        """Delete beatmap data.

        Args:
            channel_id (int): Channel ID.
        """
        await self.redis.delete(f"sunny:{channel_id}:beatmap")
