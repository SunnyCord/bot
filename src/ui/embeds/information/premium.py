###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import InteractionEmbed

if TYPE_CHECKING:
    from discord import Interaction
    from discord import Guild


class UserPremiumEmbed(InteractionEmbed):
    def __init__(self, interaction: Interaction, boosted_guilds: list[Guild]):
        super().__init__(
            interaction,
            title="Premium Information",
            description="You are a premium user. Thank you for supporting the bot!",
        )
        # TODO : this url does not exist yet
        self.add_field(
            name="Perks",
            value="You may see the perks you have unlocked [here](https://sunnycord.me/premium).",
        )

        boosted_guilds_str = "\n".join(
            [f"**{guild.name}**" for guild in boosted_guilds],
        )
        guild_plural = "guild" if len(boosted_guilds) == 1 else "guilds"

        self.add_field(
            name="Boosted Servers",
            value=f"You are currently boosting {len(boosted_guilds)} {guild_plural}.\n{boosted_guilds_str}",
            inline=False,
        )

        self.set_thumbnail(url=interaction.user.avatar)
