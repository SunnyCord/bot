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

        self.add_field(
            name="Name (ID)",
            value=f"{interaction.client.user} ({interaction.client.user.id})",
            inline=False,
        )
        self.add_field(
            name="Website",
            value="[sunnycord.me](https://sunnycord.me)",
            inline=False,
        )
        self.add_field(name="Users", value=len(interaction.client.users))
        self.add_field(name="Guilds", value=len(interaction.client.guilds))
        self.add_field(name="Commands", value=len(interaction.client.all_commands))
        self.add_field(name="Cogs", value=len(interaction.client.cogs))
        self.add_field(
            name="Created:",
            value=f"<t:{interaction.client.user.created_at.timestamp():.0f}:R>",
        )
