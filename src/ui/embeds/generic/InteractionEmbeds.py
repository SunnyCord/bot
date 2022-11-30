from __future__ import annotations

import discord


class InteractionEmbed(discord.Embed):
    def __init__(self, interaction: discord.Interaction, **kwargs):
        super().__init__(color=interaction.client.config.color, **kwargs)


class InteractionAuthorEmbed(InteractionEmbed):
    def __init__(self, interaction: discord.Interaction, **kwargs):
        super().__init__(interaction, **kwargs)
        self.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
