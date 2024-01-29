###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from typing import Any


class ContextEmbed(discord.Embed):
    def __init__(self, ctx: discord.ext.commands.Context, *args: Any, **kwargs: Any):
        super().__init__(color=ctx.bot.config.color, *args, **kwargs)

    async def prepare(self) -> None: ...


class ContextAuthorEmbed(ContextEmbed):
    def __init__(self, ctx: discord.ext.commands.Context, *args: Any, **kwargs: Any):
        super().__init__(ctx, *args, **kwargs)
        self.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
