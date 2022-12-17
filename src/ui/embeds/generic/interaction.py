from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from typing import Any


class InteractionEmbed(discord.Embed):
    def __init__(self, interaction: discord.Interaction, *args: Any, **kwargs: Any):
        super().__init__(color=interaction.client.config.color, *args, **kwargs)

    async def prepare(self) -> None:
        ...


class InteractionAuthorEmbed(InteractionEmbed):
    def __init__(self, interaction: discord.Interaction, *args: Any, **kwargs: Any):
        super().__init__(interaction, *args, **kwargs)
        self.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
