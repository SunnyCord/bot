from __future__ import annotations

import discord
from ui.embeds.generic import InteractionEmbed


class BotInfoEmbed(InteractionEmbed):
    def __init__(self, interaction, **kwargs):
        super().__init__(interaction, timestamp=interaction.created_at, **kwargs)
        self.set_thumbnail(url=interaction.client.user.avatar)
        self.set_footer(text=interaction.client.user.name)
