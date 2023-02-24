###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from discord import commands


class OsuLinkEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, link_url: str):
        super().__init__(
            ctx,
            title="osu! Profile Link",
            description=f"Click [here]({link_url}) to link your osu! profile.",
        )
        self.set_thumbnail(url=ctx.bot.user.avatar)
