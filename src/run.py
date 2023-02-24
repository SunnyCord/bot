from __future__ import annotations

import sentry_sdk
from classes.bot import Sunny

bot = Sunny()

sentry_sdk.init(bot.config.sentry)

if __name__ == "__main__":
    bot.run(reconnect=True)
