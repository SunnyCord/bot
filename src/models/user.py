from __future__ import annotations

from aiosu.models import OAuthToken
from pydantic import BaseModel


class User(BaseModel):
    discord_id: int
    blacklist: bool


class TokenDTO(BaseModel):
    discord_id: int
    osu_id: int
    token: OAuthToken
