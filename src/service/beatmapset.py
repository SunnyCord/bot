###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import Gamemode
from aiosu.models import LegacyBeatmapset

from repository.beatmapset import BeatmapsetRepository


class BeatmapsetService:
    """Service for persistent beatmapset data."""

    __slots__ = ("repository",)

    def __init__(self, repository: BeatmapsetRepository) -> None:
        self.repository = repository

    async def get_one(self, beatmapset_id: int) -> LegacyBeatmapset:
        """Get beatmapset from database.

        Args:
            beatmapset_id (int): Beatmapset ID.

        Raises:
            ValueError: Beatmapset not found.

        Returns:
            Beatmapset: Beatmapset data.
        """
        data = await self.repository.get_one(beatmapset_id)
        if data is None:
            raise ValueError("Beatmapset not found.")
        return LegacyBeatmapset.model_validate(data)

    async def get_many(self) -> list[LegacyBeatmapset]:
        """Get all beatmapsets from database.

        Returns:
            list[Beatmapset]: List of beatmapsets.
        """
        data = await self.repository.get_many()
        return [LegacyBeatmapset.model_validate(beatmapset) for beatmapset in data]

    async def get_random(self, gamemode: Gamemode) -> LegacyBeatmapset:
        """Get random beatmapset from database.

        Args:
            gamemode (Gamemode): Gamemode.

        Returns:
            Beatmapset: Beatmapset data.
        """
        data = await self.repository.get_random(gamemode.name_api)
        if not data:
            raise ValueError("Beatmapset not found.")
        return LegacyBeatmapset.model_validate(data[0])
