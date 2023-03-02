###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import InteractionEmbed

if TYPE_CHECKING:
    from discord import Interaction


class OsuLinkEmbed(InteractionEmbed):
    def __init__(self, interaction: Interaction, link_url: str):
        super().__init__(
            interaction,
            title="osu! Profile Link",
            description=f"Click [here]({link_url}) to link your osu! profile.",
        )
        self.set_thumbnail(url=interaction.client.user.avatar)
