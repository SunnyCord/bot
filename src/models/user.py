###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiosu.models import OAuthToken
from pydantic import BaseModel


class User(BaseModel):
    discord_id: int
    blacklist: bool


class TokenDTO(BaseModel):
    osu_id: int
    discord_id: int
    token: OAuthToken
