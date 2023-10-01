###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from discord import commands


class HelpEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context):
        super().__init__(
            ctx,
            title="Sunny Help",
            description="Click [here](https://sunnycord.me/commands) to view the help page!",
        )
        self.set_thumbnail(url=ctx.bot.user.avatar)
