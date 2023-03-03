###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import sentry_sdk
from classes.bot import Sunny

bot = Sunny()

sentry_sdk.init(
    dsn=bot.config.sentry,
    environment=bot.config.environment,
    traces_sample_rate=1.0,
)

if __name__ == "__main__":
    bot.run(reconnect=True)
