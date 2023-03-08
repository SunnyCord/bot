###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from discord.ext import commands


class MusicPlayerError(commands.CommandError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class WeatherAPIError(Exception):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0]
