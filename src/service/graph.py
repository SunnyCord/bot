###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from io import BytesIO

from repository.graph import GraphRepository


class GraphService:
    """Graph Service"""

    def __init__(self, repository: GraphRepository) -> None:
        self.repository = repository

    async def get_one(self, osu_id: int) -> BytesIO:
        """Get graph from Redis.

        Args:
            osu_id (int): osu! ID.

        Raises:
            ValueError: Graph not found.

        Returns:
            BytesIO: Graph.
        """
        return await self.repository.get_one(osu_id)

    async def get_many(self) -> list[BytesIO]:
        """Get all graphs from Redis.

        Returns:
            list[BytesIO]: List of graphs.
        """
        return await self.repository.get_many()

    async def add(self, osu_id: int, graph: BytesIO) -> None:
        """Add new graph to Redis.

        Args:
            osu_id (int): osu! ID.
            graph (BytesIO): Graph.
        """
        await self.repository.add(osu_id, graph)

    async def delete(self, osu_id: int) -> None:
        """Delete graph from Redis.

        Args:
            osu_id (int): osu! ID.
        """
        await self.repository.delete(osu_id)
