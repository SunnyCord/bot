###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import Beatmap
from repository.beatmap import BeatmapRepository


class BeatmapService:
    """Service for channel beatmap data."""

    def __init__(self, repository: BeatmapRepository):
        self.repository = repository

    async def get_one(self, channel_id: int) -> Beatmap:
        """Get beatmap data from database.
        Args:
            channel_id (int): Channel ID.
        Raises:
            ValueError: Beatmap not found.
        Returns:
            Beatmap: Beatmap data.
        """
        return await self.repository.get_one(channel_id)

    async def get_many(self) -> list[Beatmap]:
        """Get all beatmaps from database.
        Returns:
            list[Beatmap]: List of beatmaps.
        """
        return await self.repository.get_many()

    async def add(self, channel_id: int, beatmap: Beatmap) -> None:
        """Add new beatmap to database.
        Args:
            channel_id (int): Channel ID.
            beatmap (Beatmap): Beatmap data.
        """
        await self.repository.add(channel_id, beatmap)

    async def update(self, channel_id: int, beatmap: Beatmap) -> None:
        """Update beatmap data.
        Args:
            channel_id (int): Channel ID.
            beatmap (Beatmap): Beatmap data.
        """
        await self.repository.update(channel_id, beatmap)

    async def delete(self, channel_id: int) -> None:
        """Delete beatmap data.
        Args:
            channel_id (int): Channel ID.
        """
        await self.repository.delete(channel_id)
