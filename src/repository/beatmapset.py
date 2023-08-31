###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient


class BeatmapsetRepository:
    """Repository for persistent beatmapset data."""

    __slots__ = ("database",)

    def __init__(self, database: AsyncIOMotorClient) -> None:
        self.database = database

    async def get_one(self, beatmapset_id: int) -> dict[str, Any] | None:
        """Get beatmapset from database.

        Args:
            beatmapset_id (int): Beatmapset ID.

        Returns:
            Optional[dict[str, Any]]: Beatmapset data.
        """
        return await self.database.beatmapsets.find_one(
            {"beatmapset_id": beatmapset_id},
        )

    async def get_many(self) -> list[dict[str, Any]]:
        """Get all beatmapsets from database.

        Returns:
            list[dict[str, Any]]: List of beatmapset data.
        """
        return await self.database.beatmapsets.find().to_list(None)

    async def get_random(self, gamemode: str) -> dict[str, Any]:
        """Get random beatmapset from database.

        Args:
            gamemode (str): Gamemode name.

        Returns:
            dict[str, Any]: Beatmapset data.
        """
        return await self.database.beatmapsets.aggregate(
            [
                {"$match": {"gamemode": gamemode}},
                {"$sample": {"size": 1}},
            ],
        ).to_list(None)
