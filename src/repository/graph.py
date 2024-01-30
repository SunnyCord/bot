###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from redis.asyncio import Redis


class GraphRepository:
    """Graph Repository"""

    __slots__ = ("redis",)

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_one(
        self,
        osu_id: int,
        mode_id: int,
    ) -> bytes | None:
        """Get graph from Redis.

        Args:
            osu_id (int): osu! ID.

        Raises:
            ValueError: Graph not found.

        Returns:
            Optional[bytes]: Graph data.
        """
        return await self.redis.get(f"sunny:{osu_id}:{mode_id}:graph")

    async def get_many(self) -> list[bytes]:
        """Get all graphs from Redis.

        Returns:
            list[bytes]: List of graphs data.
        """
        keys = await self.redis.keys("sunny:*:*:graph")
        return [await self.redis.get(key) for key in keys]

    async def add(
        self,
        osu_id: int,
        graph: bytes,
        mode_id: int,
    ) -> None:
        """Add new graph to Redis.

        Args:
            osu_id (int): osu! ID.
            graph (bytes): Graph.
        """
        await self.redis.set(
            f"sunny:{osu_id}:{mode_id}:graph",
            graph,
            ex=86400,
        )

    async def delete(self, osu_id: int, mode_id: int) -> None:
        """Delete graph from Redis.

        Args:
            osu_id (int): osu! ID.
        """
        await self.redis.delete(f"sunny:{osu_id}:{mode_id}:graph")
