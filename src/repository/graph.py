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
        lazer: bool = False,
    ) -> bytes | None:
        """Get graph from Redis.

        Args:
            osu_id (int): osu! ID.
            lazer (bool, optional): Lazer graph. Defaults to False.

        Raises:
            ValueError: Graph not found.

        Returns:
            Optional[bytes]: Graph data.
        """
        if lazer:
            graph = await self.redis.get(f"sunny:{osu_id}:{mode_id}:lazer:graph")
        else:
            graph = await self.redis.get(f"sunny:{osu_id}:{mode_id}:graph")
        return graph

    async def get_many(self, lazer: bool = False) -> list[bytes]:
        """Get all graphs from Redis.

        Args:
            lazer (bool, optional): Lazer graph. Defaults to False.

        Returns:
            list[bytes]: List of graphs data.
        """
        if lazer:
            keys = await self.redis.keys("sunny:*:*:lazer:graph")
        else:
            keys = await self.redis.keys("sunny:*:*:graph")
        return [await self.redis.get(key) for key in keys]

    async def add(
        self,
        osu_id: int,
        graph: bytes,
        mode_id: int,
        lazer: bool = False,
    ) -> None:
        """Add new graph to Redis.

        Args:
            osu_id (int): osu! ID.
            graph (bytes): Graph.
            lazer (bool, optional): Lazer graph. Defaults to False.
        """
        if lazer:
            await self.redis.set(
                f"sunny:{osu_id}:{mode_id}:lazer:graph",
                graph,
                ex=86400,
            )
        else:
            await self.redis.set(
                f"sunny:{osu_id}:{mode_id}:graph",
                graph,
                ex=86400,
            )

    async def delete(self, osu_id: int, mode_id: int, lazer: bool = False) -> None:
        """Delete graph from Redis.

        Args:
            osu_id (int): osu! ID.
            lazer (bool, optional): Lazer graph. Defaults to False.
        """
        if lazer:
            await self.redis.delete(f"sunny:{osu_id}:{mode_id}:lazer:graph")
        else:
            await self.redis.delete(f"sunny:{osu_id}:{mode_id}:graph")
