###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from io import BytesIO

from redis.asyncio import Redis


class GraphRepository:
    """Graph Repository"""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_one(self, osu_id: int) -> BytesIO:
        """Get graph from Redis.

        Args:
            osu_id (int): osu! ID.

        Raises:
            ValueError: Graph not found.

        Returns:
            BytesIO: Graph.
        """
        graph = await self.redis.get(f"sunny:{osu_id}:graph")
        if graph is None:
            raise ValueError("Graph not found.")
        return BytesIO(graph)

    async def get_many(self) -> list[BytesIO]:
        """Get all graphs from Redis.

        Returns:
            list[BytesIO]: List of graphs.
        """
        graphs = await self.redis.keys("sunny:*:graph")
        return [BytesIO(graph) for graph in graphs]

    async def add(self, osu_id: int, graph: BytesIO) -> None:
        """Add new graph to Redis.

        Args:
            osu_id (int): osu! ID.
            graph (BytesIO): Graph.
        """
        await self.redis.set(
            f"sunny:{osu_id}:graph",
            graph.getvalue(),
            ex=86400,
        )

    async def delete(self, osu_id: int) -> None:
        """Delete graph from Redis.

        Args:
            osu_id (int): osu! ID.
        """
        await self.redis.delete(f"sunny:{osu_id}:graph")
