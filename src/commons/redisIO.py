from __future__ import annotations

import redis


class redisIO:
    def __init__(self, bot):
        self.config = bot.config
        self.db = redis.Redis(
            host=bot.config.redis.host,
            port=bot.config.redis.port,
            db=0,
            decode_responses=True,
        )

    def getValue(self, name):
        return self.db.get(name)

    def setValue(self, name, value):
        self.db.set(name, value)
