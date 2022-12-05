from __future__ import annotations

from typing import TYPE_CHECKING

import redis

if TYPE_CHECKING:
    from typing import Any
    from classes.bot import Sunny


class redisIO:
    def __init__(self, bot: Sunny) -> None:
        self.config = bot.config
        self.db = redis.Redis(
            host=bot.config.redis.host,
            port=bot.config.redis.port,
            db=0,
            decode_responses=True,
        )

    def getValue(self, name: str) -> Any:
        return self.db.get(name)

    def setValue(self, name: str, value: Any) -> None:
        self.db.set(name, value)
