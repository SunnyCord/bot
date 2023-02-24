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
            description="Click [here](https://github.com/SunnyCord/bot/wiki/Commands) to view the help page!",
        )
        self.set_thumbnail(url=ctx.bot.user.avatar)
