###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import json

from aiosu.models import BeatmapExtended
from aiosu.models import LegacyBeatmap

from repository.beatmap import BeatmapRepository

type CachedBeatmap = BeatmapExtended | LegacyBeatmap


def _load_beatmap(data: str) -> CachedBeatmap:
    record = json.loads(data)
    if "mode_int" in record:
        return BeatmapExtended.model_validate(record)
    record.setdefault("lazer_only", False)
    record.pop("beatmapset", None)
    return LegacyBeatmap.model_validate(record)


class BeatmapService:
    """Service for channel beatmap data."""

    __slots__ = ("repository",)

    def __init__(self, repository: BeatmapRepository) -> None:
        self.repository = repository

    async def get_one(self, channel_id: int) -> CachedBeatmap:
        """Get beatmap data from database.
        Args:
            channel_id (int): Channel ID.
        Raises:
            ValueError: Beatmap not found.
        Returns:
            Beatmap: Beatmap data.
        """
        data = await self.repository.get_one(channel_id)
        if data is None:
            raise ValueError("Beatmap not found.")
        return _load_beatmap(data)

    async def get_many(self) -> list[CachedBeatmap]:
        """Get all beatmaps from database.
        Returns:
            list[Beatmap]: List of beatmaps.
        """
        data = await self.repository.get_many()
        return [_load_beatmap(beatmap) for beatmap in data]

    async def add(self, channel_id: int, beatmap: CachedBeatmap) -> None:
        """Add new beatmap to database.
        Args:
            channel_id (int): Channel ID.
            beatmap (Beatmap): Beatmap data.
        """
        data = beatmap.model_dump_json()
        await self.repository.add(channel_id, data)

    async def update(self, channel_id: int, beatmap: CachedBeatmap) -> None:
        """Update beatmap data.
        Args:
            channel_id (int): Channel ID.
            beatmap (Beatmap): Beatmap data.
        """
        data = beatmap.model_dump_json()
        await self.repository.update(channel_id, data)

    async def delete(self, channel_id: int) -> None:
        """Delete beatmap data.
        Args:
            channel_id (int): Channel ID.
        """
        await self.repository.delete(channel_id)
