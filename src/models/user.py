###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from dataclasses import dataclass

from aiosu.models import OAuthToken
from aiosu.models import User
from aiosu.v2 import Client
from pydantic import BaseModel


class DatabaseUser(BaseModel):
    discord_id: int
    blacklist: bool


class TokenDTO(BaseModel):
    osu_id: int
    discord_id: int
    token: OAuthToken


@dataclass
class UserConverterDTO:
    client: Client
    user: DatabaseUser
    is_app_client: bool = False
    lazer: bool = False
    author_client: Client | None = None
