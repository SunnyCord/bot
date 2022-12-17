from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from classes.deprecated.server import Server


class DatabaseMissingError(Exception):
    def __init__(self, queryType: str, message: str = "") -> None:
        super().__init__(message)
        self.queryType = queryType


class MusicPlayerError(commands.CommandError):
    def __init(self, message: str = "") -> None:
        super().__init__(message)
