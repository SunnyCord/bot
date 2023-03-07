###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from typing import Any
    from discord.ext.commands import Context


class BotInfoEmbed(ContextEmbed):
    def __init__(self, ctx: Context, *args: Any, **kwargs: Any) -> None:
        super().__init__(ctx, timestamp=ctx.message.created_at, *args, **kwargs)
        self.set_thumbnail(url=ctx.bot.user.avatar)
        self.set_footer(text=ctx.bot.user.name)

        self.add_field(
            name="Name (ID)",
            value=f"{ctx.bot.user} ({ctx.bot.user.id})",
            inline=False,
        )
        self.add_field(
            name="Website",
            value="[sunnycord.me](https://sunnycord.me)",
            inline=False,
        )
        self.add_field(name="Users", value=len(ctx.bot.users))
        self.add_field(name="Guilds", value=len(ctx.bot.guilds))
        self.add_field(name="Commands", value=len(ctx.bot.all_commands))
        self.add_field(name="Cogs", value=len(ctx.bot.cogs))
        self.add_field(
            name="Created:",
            value=f"<t:{ctx.bot.user.created_at.timestamp():.0f}:R>",
        )
