###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from pydantic import BaseModel


class GuildSettings(BaseModel):
    guild_id: int
    prefix: str = ""
