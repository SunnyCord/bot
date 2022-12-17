from __future__ import annotations

from discord.ext import commands


class DatabaseMissingError(Exception):
    def __init__(self, queryType: str, message: str = "") -> None:
        super().__init__(message)
        self.queryType = queryType


class MusicPlayerError(commands.CommandError):
    def __init(self, message: str = "") -> None:
        super().__init__(message)
