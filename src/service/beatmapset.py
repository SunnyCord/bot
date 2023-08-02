###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import Beatmapset
from aiosu.models import Gamemode
from repository.beatmapset import BeatmapsetRepository


class BeatmapsetService:
    """Service for persistent beatmapset data."""

    __slots__ = ("repository",)

    def __init__(self, repository: BeatmapsetRepository):
        self.repository = repository

    async def get_one(self, beatmapset_id: int) -> Beatmapset:
        """Get beatmapset from database.

        Args:
            beatmapset_id (int): Beatmapset ID.

        Raises:
            ValueError: Beatmapset not found.

        Returns:
            Beatmapset: Beatmapset data.
        """
        return await self.repository.get_one(beatmapset_id)

    async def get_many(self) -> list[Beatmapset]:
        """Get all beatmapsets from database.

        Returns:
            list[Beatmapset]: List of beatmapsets.
        """
        return await self.repository.get_many()

    async def get_random(self, gamemode: Gamemode) -> Beatmapset:
        """Get random beatmapset from database.

        Args:
            gamemode (Gamemode): Gamemode.

        Returns:
            Beatmapset: Beatmapset data.
        """
        return await self.repository.get_random(gamemode)
