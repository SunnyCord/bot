from __future__ import annotations

import logging

import sentry_sdk

from classes.bot import Sunny

logger = logging.getLogger()
bot = Sunny()
sentry_sdk.init(bot.config.sentry)

if __name__ == "__main__":
    bot.run(reconnect=True)
