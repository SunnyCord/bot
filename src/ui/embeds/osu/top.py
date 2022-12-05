from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed
from ui.emojis.score import ScoreRankIcon

if TYPE_CHECKING:
    import aiosu
    from discord import commands


class OsuTopsEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        tops: list[aiosu.classes.Score],
    ):
        super().__init__(ctx)
        self.ctx = ctx
        self.prepared = False
        self.tops = tops

    async def prepare(self):
        if not self.prepared:
            for score in self.tops:
                await score.request_beatmap(self.ctx.bot.client_v1)
                beatmap, beatmapset = score.beatmap, score.beatmapset
                title = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"

                self.add_field(
                    name=title,
                    value=ScoreRankIcon[score.rank],
                    inline=False,
                )
            self.prepared = True
