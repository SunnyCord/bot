###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from pydantic import BaseModel


class UserPreferences(BaseModel):
    discord_id: int
    lazer: bool = False
