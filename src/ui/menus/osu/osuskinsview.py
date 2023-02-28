###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle
from discord.ui import button
from ui.embeds.osu import OsuSkinEmbed
from ui.menus.generic import BaseInteractionView

if TYPE_CHECKING:
    from typing import Any
    from aiordr.models import Skin
    from discord import Interaction
    from classes.bot import Sunny


def _split_skins_to_pages(
    interaction: Interaction,
    skins: list[Skin],
) -> list[OsuSkinEmbed]:
    embeds: list[OsuSkinEmbed] = [OsuSkinEmbed(interaction, skin) for skin in skins]

    return embeds


class OsuSkinsView(BaseInteractionView):
    def __init__(
        self,
        interaction: Interaction,
        skins: list[Skin],
        *args: Any,
        **kwargs: Any,
    ):
        self.interaction = interaction
        self.author = interaction.user
        self.bot: Sunny = interaction.client

        super().__init__(*args, **kwargs)

        self._current = 0
        self._embeds = _split_skins_to_pages(interaction, skins)

        for i, embed in enumerate(self._embeds):
            embed.set_footer(text=f"Skin {i+1}/{self._len}")

        if self._len <= 1:
            self.remove_item(self.first_embed_button)
            self.remove_item(self.previous_embed_button)
            self.remove_item(self.next_embed_button)
            self.remove_item(self.last_embed_button)
        else:
            self._check_buttons()

    @property
    def initial(self) -> OsuSkinEmbed:
        return self._embeds[0]

    @property
    def _len(self) -> int:
        return len(self._embeds)

    def _get_embed(self) -> OsuSkinEmbed:
        return self._embeds[self._current]

    def _check_buttons(self) -> None:
        if self._current == 0:
            self.first_embed_button.disabled = True
        else:
            self.first_embed_button.disabled = False
        if self._current == self._len - 1:
            self.last_embed_button.disabled = True
        else:
            self.last_embed_button.disabled = False

    def _previous_embed(self) -> None:
        self._current = (self._current - 1) % self._len
        self._check_buttons()

    def _next_embed(self) -> None:
        self._current = (self._current + 1) % self._len
        self._check_buttons()

    def _stop(self) -> None:
        self.clear_items()
        self.stop()

    @button(emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}")
    async def first_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._current = 0
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._previous_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="\N{WHITE HEAVY CHECK MARK}")
    async def select_skin(
        self,
        interaction: Interaction,
        button: button.Button,
        style=ButtonStyle.green,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        embed = self._get_embed()
        await interaction.response.edit_message(
            content=f"Skin **{embed.skin.presentation_name}** selected!",
            embed=embed,
        )
        await self.bot.recording_prefs_service.set_option(
            interaction.user.id,
            "skin",
            embed.skin.name,
        )

    @button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._next_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
    async def last_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._current = self._len - 1
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)
