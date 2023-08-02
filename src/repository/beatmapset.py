###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import Beatmapset
from aiosu.models import Gamemode
from motor.motor_asyncio import AsyncIOMotorClient


class BeatmapsetRepository:
    """Repository for persistent beatmapset data."""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorClient) -> None:
        self.database = database

    async def get_one(self, beatmapset_id: int) -> Beatmapset:
        """Get beatmapset from database.

        Args:
            beatmapset_id (int): Beatmapset ID.

        Raises:
            ValueError: Beatmapset not found.

        Returns:
            Beatmapset: Beatmapset data.
        """
        beatmapset = await self.database.beatmapsets.find_one(
            {"beatmapset_id": beatmapset_id},
        )
        if beatmapset is None:
            raise ValueError("Beatmapset not found.")
        return Beatmapset.model_validate(beatmapset)

    async def get_many(self) -> list[Beatmapset]:
        """Get all beatmapsets from database.

        Returns:
            list[Beatmapset]: List of beatmapsets.
        """
        beatmapsets = await self.database.beatmapsets.find().to_list(None)
        return [Beatmapset.model_validate(beatmapset) for beatmapset in beatmapsets]

    async def get_random(self, gamemode: Gamemode) -> Beatmapset:
        """Get random beatmapset from database.

        Args:
            gamemode (Gamemode): Gamemode.

        Returns:
            Beatmapset: Beatmapset data.
        """
        beatmapset = await self.database.beatmapsets.aggregate(
            [
                {"$match": {"gamemode": gamemode.name_api}},
                {"$sample": {"size": 1}},
            ],
        ).to_list(None)
        return Beatmapset.model_validate(beatmapset[0])
