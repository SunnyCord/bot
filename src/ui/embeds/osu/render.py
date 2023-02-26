###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from discord import commands


class OsuRenderEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, title: str, description: str):
        super().__init__(
            ctx,
            title=title,
            description=description,
        )
        self.set_thumbnail(url=ctx.bot.user.avatar)
