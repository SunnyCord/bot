###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from io import BytesIO

from repository.graph import GraphRepository


class GraphService:
    """Graph Service"""

    __slots__ = ("repository",)

    def __init__(self, repository: GraphRepository) -> None:
        self.repository = repository

    async def get_one(self, osu_id: int, mode_id: int, lazer: bool = False) -> BytesIO:
        """Get graph from Redis.

        Args:
            osu_id (int): osu! ID.
            lazer (bool, optional): Lazer graph. Defaults to False.

        Raises:
            ValueError: Graph not found.

        Returns:
            BytesIO: Graph.
        """
        data = await self.repository.get_one(osu_id, mode_id, lazer)
        if data is None:
            raise ValueError("Graph not found.")
        return BytesIO(data)

    async def get_many(self, lazer: bool = False) -> list[BytesIO]:
        """Get all graphs from Redis.

        Args:
            lazer (bool, optional): Lazer graph. Defaults to False.

        Returns:
            list[BytesIO]: List of graphs.
        """
        data = await self.repository.get_many(lazer)
        return [BytesIO(graph) for graph in data]

    async def add(
        self,
        osu_id: int,
        graph: BytesIO,
        mode_id: int,
        lazer: bool = False,
    ) -> None:
        """Add new graph to Redis.

        Args:
            osu_id (int): osu! ID.
            graph (BytesIO): Graph.
            lazer (bool, optional): Lazer graph. Defaults to False.
        """
        await self.repository.add(osu_id, graph.getvalue(), mode_id, lazer)

    async def delete(self, osu_id: int, mode_id: int, lazer: bool = False) -> None:
        """Delete graph from Redis.

        Args:
            osu_id (int): osu! ID.
            lazer (bool, optional): Lazer graph. Defaults to False.
        """
        await self.repository.delete(osu_id, mode_id, lazer)
