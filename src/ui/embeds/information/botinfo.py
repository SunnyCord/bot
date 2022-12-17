from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import InteractionEmbed

if TYPE_CHECKING:
    from typing import Any
    from discord import Interaction


class BotInfoEmbed(InteractionEmbed):
    def __init__(self, interaction: Interaction, *args: Any, **kwargs: Any) -> None:
        super().__init__(interaction, timestamp=interaction.created_at, *args, **kwargs)
        self.set_thumbnail(url=interaction.client.user.avatar)
        self.set_footer(text=interaction.client.user.name)
