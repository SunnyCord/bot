###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from aiordr.models import RenderOptions
from models.weather import Units
from pydantic import BaseModel


class UserPreferences(BaseModel):
    discord_id: int
    lazer: bool = False
    units: Units = Units.METRIC


class RecordingPreferences(RenderOptions):
    discord_id: int
    skin: str = "YUGEN"

    def get_render_options(self) -> RenderOptions:
        return RenderOptions.model_validate(self.model_dump(exclude_defaults=True))
