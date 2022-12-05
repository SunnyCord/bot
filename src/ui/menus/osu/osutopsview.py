from __future__ import annotations

from collections import deque

from aiosu.classes import Score
from discord import Embed
from discord import Interaction
from discord.ui import button
from ui.embeds.osu import OsuTopsEmbed
from ui.menus.generic import BaseView


def _split_tops_to_pages(
    ctx,
    tops: list[Score],
    per_page: int = 3,
) -> list[OsuTopsEmbed]:
    top_count = len(tops)
    embeds: list[OsuTopsEmbed] = [
        OsuTopsEmbed(ctx, tops[x : x + per_page]) for x in range(0, top_count, per_page)
    ]
    return embeds


class OsuTopsView(BaseView):
    def __init__(self, ctx, user, mode, tops: list[Score], recent: bool, **kwargs):
        super().__init__(**kwargs)

        per_page = 3
        embeds = _split_tops_to_pages(ctx, tops, per_page)
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        for i, embed in enumerate(embeds):
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(
                name=f"{'Recent ' if recent else ''}osu! {mode:f} top plays for {user.username}",
                url=user.url,
            )
            embed.set_footer(text=f"Page {i+1}/{self._len}")

    @button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed(self, interaction: Interaction, _):
        self._queue.rotate(1)
        embed = self._queue[0]
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)

    @button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed(self, interaction: Interaction, _):
        self._queue.rotate(-1)
        embed = self._queue[0]
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> Embed:
        return self._initial
