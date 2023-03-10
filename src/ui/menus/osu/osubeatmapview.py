###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction
from discord.ui import button
from ui.embeds.osu import OsuBeatmapEmbed
from ui.menus.generic import BaseView

if TYPE_CHECKING:
    from typing import Any
    from aiosu.models import Beatmapset
    from discord.ext.commands import Context


def _split_beatmapset_to_pages(
    ctx: Context,
    beatmapset: Beatmapset,
) -> list[OsuBeatmapEmbed]:
    embeds: list[OsuBeatmapEmbed] = [
        OsuBeatmapEmbed(ctx, beatmapset, beatmap) for beatmap in beatmapset.beatmaps
    ]

    return embeds


class OsuBeatmapView(BaseView):
    __slots__ = (
        "ctx",
        "bot",
        "author",
        "_embeds",
        "_current",
    )

    def __init__(
        self,
        ctx: Context,
        beatmapset: Beatmapset,
        *args: Any,
        **kwargs: Any,
    ):
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author

        super().__init__(*args, **kwargs)

        self._embeds = _split_beatmapset_to_pages(self.ctx, beatmapset)
        self._current = 0

        for i, embed in enumerate(self._embeds):
            embed.set_footer(text=f"Difficulty {i+1}/{self._len}")

        if self._len <= 1:
            self._stop()
        else:
            self._check_buttons()

    @property
    def initial(self) -> OsuBeatmapEmbed:
        return self._embeds[0]

    @property
    def _len(self) -> int:
        return len(self._embeds)

    def _get_embed(self) -> OsuBeatmapEmbed:
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
                delete_after=10,
            )
            return
        self._current = 0
        self._check_buttons()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)

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
                delete_after=10,
            )
            return
        self._previous_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)

    @button(emoji="\N{BLACK SQUARE FOR STOP}")
    async def stop_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
                delete_after=10,
            )
            return
        self._stop()
        await interaction.response.edit_message(view=self)

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
                delete_after=10,
            )
            return
        self._next_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)

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
                delete_after=10,
            )
            return
        self._current = self._len - 1
        self._check_buttons()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)
