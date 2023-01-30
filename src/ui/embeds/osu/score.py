from __future__ import annotations

from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed
from ui.emojis.score import ScoreRankIcon

if TYPE_CHECKING:
    from typing import Any
    import aiosu
    from discord import commands


def _score_to_embed_strs(
    score: aiosu.models.Score,
    include_user: bool = False,
) -> dict[str, str]:
    beatmap, beatmapset = score.beatmap, score.beatmapset
    name = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"

    weight = ""
    score_text = ""

    if score.weight:
        weight += f" (weight {score.weight.percentage/100:.2f})"
    if score_url := score.score_url:
        score_text += f"[score]({score_url}) | "
    if include_user:
        score_text += f"[user](https://osu.ppy.sh/users/{score.user_id}) | "

    value = f"""**{score.pp:.2f}pp**{weight}, accuracy: **{score.accuracy*100:.2f}%**, combo: **{score.max_combo}x/{beatmap.max_combo}x**
            score: **{score.score}** [**{score.statistics.count_300}**/**{score.statistics.count_100}**/**{score.statistics.count_50}**/**{score.statistics.count_miss}**]
            mods: {score.mods} | {ScoreRankIcon[score.rank]}
            <t:{score.created_at.timestamp():.0f}:R>
            {score_text}[map]({beatmap.url})
    """
    return {"name": name, "value": value}


class OsuScoreSingleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        score: aiosu.models.Score,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, *args, **kwargs)
        self.ctx = ctx
        self.prepared = False
        self.score = score

    async def prepare(self) -> None:
        await self.score.request_beatmap(self.ctx.bot.client_v1)
        self.set_thumbnail(url=self.score.beatmapset.covers.list)

        self.add_field(inline=False, **_score_to_embed_strs(self.score, True))


class OsuScoreMultipleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        scores: list[aiosu.models.Score],
        same_beatmap: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, *args, **kwargs)
        self.ctx = ctx
        self.prepared = False
        self.scores = scores
        self.same_beatmap = same_beatmap

    async def prepare(self) -> None:
        if not self.prepared:
            if self.same_beatmap:
                await self.scores[0].request_beatmap(self.ctx.bot.client_v1)
                beatmapset = self.scores[0].beatmapset
                self.set_thumbnail(url=beatmapset.covers.list)

            for score in self.scores:
                if self.same_beatmap:
                    score.beatmap = self.scores[0].beatmap
                    score.beatmapset = self.scores[0].beatmapset
                else:
                    await score.request_beatmap(self.ctx.bot.client_v1)

                data = _score_to_embed_strs(score, False)
                if self.same_beatmap:
                    data["name"] = "_ _"

                self.add_field(inline=False, **data)
            self.prepared = True
