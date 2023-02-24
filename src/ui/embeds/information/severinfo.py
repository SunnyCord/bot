###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from ui.embeds.generic import InteractionEmbed

if TYPE_CHECKING:
    from typing import Any


class ServerInfoEmbed(InteractionEmbed):
    def __init__(
        self, interaction: discord.Interaction, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(interaction, timestamp=interaction.created_at, *args, **kwargs)
        self.set_thumbnail(url=interaction.guild.icon)
        self.set_footer(
            text=interaction.client.user.name,
            icon_url=interaction.client.user.avatar,
        )

        self.add_field(
            name="Name (ID)",
            value=f"{interaction.guild} ({interaction.guild.id})",
            inline=False,
        )
        self.add_field(name="Owner", value=interaction.guild.owner, inline=False)
        self.add_field(
            name="Verification Level",
            value=interaction.guild.verification_level,
        )
        self.add_field(name="Members", value=interaction.guild.member_count)
        self.add_field(
            name="Text Channels",
            value=len(
                list(
                    filter(
                        lambda x: isinstance(x, discord.channel.TextChannel),
                        interaction.guild.channels,
                    ),
                ),
            ),
        )
        self.add_field(name="Roles", value=len(interaction.guild.roles))
        self.add_field(name="Emotes", value=len(interaction.guild.emojis))
        self.add_field(
            name="Created On:",
            value=f"<t:{interaction.guild.created_at.timestamp():.0f}:R>",
        )
