###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import logging

logger = logging.getLogger("sunny")
discord_logger = logging.getLogger("discord")
lavalink_logger = logging.getLogger("pomice")


class Formatter(logging.Formatter):
    cyan = "\x1b[36;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_fmt = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + log_fmt + reset,
        logging.INFO: cyan + log_fmt + reset,
        logging.WARNING: yellow + log_fmt + reset,
        logging.ERROR: red + log_fmt + reset,
        logging.CRITICAL: bold_red + log_fmt + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(Formatter())
    return handler


def init_logging(level: str = "INFO"):
    handler = get_handler()
    discord_logger.setLevel(level)
    discord_logger.addHandler(handler)
    lavalink_logger.setLevel(level)
    lavalink_logger.addHandler(handler)
    logger.setLevel(level)
    logger.addHandler(handler)
