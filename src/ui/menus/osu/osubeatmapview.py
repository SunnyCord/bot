###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed
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
    def __init__(
        self,
        ctx: Context,
        beatmapset: Beatmapset,
        *args: Any,
        **kwargs: Any,
    ):
        self.ctx = ctx
        self.message = ctx.message
        self.bot = ctx.bot

        super().__init__(*args, **kwargs)

        self._embeds = _split_beatmapset_to_pages(self.ctx, beatmapset)
        self._current = 0

        for i, embed in enumerate(self._embeds):
            embed.set_footer(text=f"Difficulty {i+1}/{self._len}")

        if self._len <= 1:
            self._stop()

    @property
    def initial(self) -> OsuBeatmapEmbed:
        return self._embeds[0]

    @property
    def _len(self) -> int:
        return len(self._embeds)

    def _get_embed(self) -> OsuBeatmapEmbed:
        return self._embeds[self._current]

    def _previous_embed(self) -> None:
        self._current = (self._current - 1) % self._len

    def _next_embed(self) -> None:
        self._current = (self._current + 1) % self._len

    def _stop(self) -> None:
        self.clear_items()
        self.stop()

    @button(emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}")
    async def first_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._current = 0
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)

    @button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._previous_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)

    @button(emoji="\N{BLACK SQUARE FOR STOP}")
    async def stop_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._stop()
        await interaction.response.edit_message(view=self)

    @button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._next_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)

    @button(emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
    async def last_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._current = self._len - 1
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)
