from __future__ import annotations

from typing import TYPE_CHECKING

from aioredis import Redis

if TYPE_CHECKING:
    from classes.bot import Sunny


class redisIO(Redis):
    def __init__(self, bot: Sunny) -> None:
        super().__init__(
            host=bot.config.redis.host,
            port=bot.config.redis.port,
            db=0,
            decode_responses=True,
        )
