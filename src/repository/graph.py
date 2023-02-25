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

    async def get_one(self, osu_id: int, lazer: bool = False) -> BytesIO:
        """Get graph from Redis.

        Args:
            osu_id (int): osu! ID.
            lazer (bool, optional): Lazer graph. Defaults to False.

        Raises:
            ValueError: Graph not found.

        Returns:
            BytesIO: Graph.
        """
        if lazer:
            graph = await self.redis.get(f"sunny:{osu_id}:lazer:graph")
        else:
            graph = await self.redis.get(f"sunny:{osu_id}:graph")
        if graph is None:
            raise ValueError("Graph not found.")
        return BytesIO(graph)

    async def get_many(self, lazer: bool = False) -> list[BytesIO]:
        """Get all graphs from Redis.

        Args:
            lazer (bool, optional): Lazer graph. Defaults to False.

        Returns:
            list[BytesIO]: List of graphs.
        """
        if lazer:
            graphs = await self.redis.keys("sunny:*:lazer:graph")
        else:
            graphs = await self.redis.keys("sunny:*:graph")
        return [BytesIO(graph) for graph in graphs]

    async def add(self, osu_id: int, graph: BytesIO, lazer: bool = False) -> None:
        """Add new graph to Redis.

        Args:
            osu_id (int): osu! ID.
            graph (BytesIO): Graph.
            lazer (bool, optional): Lazer graph. Defaults to False.
        """
        if lazer:
            await self.redis.set(
                f"sunny:{osu_id}:lazer:graph",
                graph.getvalue(),
                ex=86400,
            )
        else:
            await self.redis.set(
                f"sunny:{osu_id}:graph",
                graph.getvalue(),
                ex=86400,
            )

    async def delete(self, osu_id: int, lazer: bool = False) -> None:
        """Delete graph from Redis.

        Args:
            osu_id (int): osu! ID.
            lazer (bool, optional): Lazer graph. Defaults to False.
        """
        if lazer:
            await self.redis.delete(f"sunny:{osu_id}:lazer:graph")
        else:
            await self.redis.delete(f"sunny:{osu_id}:graph")
