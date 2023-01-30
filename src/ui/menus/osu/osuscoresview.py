from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from discord import Embed
from discord import Interaction
from discord.ui import button
from ui.embeds.osu import OsuScoreMultipleEmbed
from ui.menus.generic import BaseView

if TYPE_CHECKING:
    from typing import Any
    from aiosu.models import User
    from aiosu.models import Score
    from aiosu.models import Gamemode
    from discord.commands import Context


def _split_tops_to_pages(
    ctx: Context,
    tops: list[Score],
    same_beatmap: bool,
    per_page: int = 3,
) -> list[OsuScoreMultipleEmbed]:
    top_count = len(tops)
    embeds: list[OsuScoreMultipleEmbed] = [
        OsuScoreMultipleEmbed(ctx, tops[x : x + per_page], same_beatmap)
        for x in range(0, top_count, per_page)
    ]
    return embeds


class OsuScoresView(BaseView):
    def __init__(
        self,
        ctx: Context,
        user: User,
        mode: Gamemode,
        tops: list[Score],
        title: str,
        same_beatmap: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        per_page = 3
        embeds = _split_tops_to_pages(ctx, tops, same_beatmap, per_page)
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        for i, embed in enumerate(embeds):
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(name=title, url=user.url)
            embed.set_footer(text=f"Page {i+1}/{self._len}")

    @button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        self._queue.rotate(1)
        embed = self._queue[0]
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)

    @button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed(self, interaction: Interaction, button: button.Button) -> None:
        self._queue.rotate(-1)
        embed = self._queue[0]
        await embed.prepare()
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> Embed:
        return self._initial
