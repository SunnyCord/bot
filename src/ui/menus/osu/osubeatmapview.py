from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from discord import Embed
from discord import Interaction
from discord import Message
from discord.ui import button
from ui.embeds.osu import OsuBeatmapEmbed
from ui.menus.generic import BaseMessageView

if TYPE_CHECKING:
    from typing import Any
    from classes.bot import Sunny
    from aiosu.models import Beatmapset


def _split_beatmapset_to_pages(
    bot: Sunny,
    beatmapset: Beatmapset,
) -> list[OsuBeatmapEmbed]:
    color = bot.config.color
    embeds: list[OsuBeatmapEmbed] = [
        OsuBeatmapEmbed(beatmapset, beatmap, color=color)
        for beatmap in beatmapset.beatmaps
    ]

    return embeds


class OsuBeatmapView(BaseMessageView):
    def __init__(
        self,
        message: Message,
        bot: Sunny,
        beatmapset: Beatmapset,
        *args: Any,
        **kwargs: Any,
    ):
        self.message = message
        self.bot = bot

        super().__init__(*args, **kwargs)

        embeds = _split_beatmapset_to_pages(bot, beatmapset)
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)

        for i, embed in enumerate(embeds):
            embed.set_footer(text=f"Difficulty {i+1}/{self._len}")

    @button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._queue.rotate(1)
        embed = self._queue[0]
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)
        await interaction.response.edit_message(embed=embed)

    @button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed(self, interaction: Interaction, button: button.Button) -> None:
        self._queue.rotate(-1)
        embed = self._queue[0]
        await self.bot.beatmap_service.add(self.message.channel.id, embed.beatmap)
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> Embed:
        return self._initial
