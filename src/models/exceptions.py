from __future__ import annotations

from discord.ext import commands


class MusicPlayerError(commands.CommandError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)
