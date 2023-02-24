###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from inspect import cleandoc
from typing import TYPE_CHECKING

from aiosu.models import LazerScore
from aiosu.utils.performance import get_calculator
from ui.embeds.generic import ContextEmbed
from ui.icons.score import ScoreRankIcon

if TYPE_CHECKING:
    from typing import Any
    import aiosu
    from discord import commands


def _score_to_embed_strs(
    score: aiosu.models.Score,
    include_user: bool = False,
    difficulty_attrs: aiosu.models.BeatmapDifficultyAttributes = None,
) -> dict[str, str]:
    beatmap, beatmapset = score.beatmap, score.beatmapset
    name = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"
    max_combo = beatmap.max_combo
    pp = score.pp

    if difficulty_attrs:
        name += f" ({difficulty_attrs.star_rating:.2f}★)"
        max_combo = difficulty_attrs.max_combo
        if not pp:
            calculator_type = get_calculator(score.mode)
            pp = calculator_type(difficulty_attrs).calculate(score).total

    weight = ""
    score_text = ""
    mods_text = score.mods
    mods_settings_text = ""
    if isinstance(score, LazerScore):
        mods_text = score.mods_str
        mods_settings_text = "\n"
        for mod in score.mods:
            for key, value in mod.settings.items():
                mods_settings_text += f"{key.replace('_', ' ')}: {value}\n"
        mods_settings_text = mods_settings_text.rstrip()

    if score.weight:
        weight += f" (weight {score.weight.percentage/100:.2f})"
    if score_url := score.score_url:
        score_text += f"[score]({score_url}) | "
    if include_user:
        score_text += f"[user](https://osu.ppy.sh/users/{score.user_id}) | "

    fail_text = ""
    if score.rank == "F":
        fail_text = f" ({score.completion:.2f}%)"

    value = cleandoc(
        f"""**{pp:.2f}pp**{weight}, accuracy: **{score.accuracy*100:.2f}%**, combo: **{score.max_combo}x/{max_combo}x**
            score: **{score.score}** [**{score.statistics.count_300}**/**{score.statistics.count_100}**/**{score.statistics.count_50}**/**{score.statistics.count_miss}**]
            mods: {mods_text} | {ScoreRankIcon[score.rank]}{fail_text}{mods_settings_text}
            <t:{score.created_at.timestamp():.0f}:R>
            {score_text}[map]({beatmap.url})
        """,
    )
    return {"name": name, "value": value}


class OsuScoreSingleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        score: aiosu.models.Score,
        title: str = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, *args, **kwargs)
        self.ctx = ctx
        self.prepared = False
        self.score = score

        self.set_thumbnail(url=self.score.beatmapset.covers.list)
        self.set_author(
            name=title or self.score.user.username,
            icon_url=self.score.user.avatar_url,
        )

    async def prepare(self) -> None:
        if self.prepared:
            return

        client = await self.ctx.bot.client_storage.app_client

        difficulty_attrs = await client.get_beatmap_attributes(
            self.score.beatmap.id,
            mods=self.score.mods,
            mode=self.score.mode,
        )

        self.add_field(
            inline=False, **_score_to_embed_strs(self.score, True, difficulty_attrs)
        )

        self.prepared = True


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
        self.difficulty_attrs = []
        self.same_beatmap = same_beatmap

    async def prepare(self) -> None:
        if self.prepared:
            return

        client = await self.ctx.bot.client_storage.app_client

        if self.same_beatmap:
            score = self.scores[0]
            if not score.beatmapset:
                beatmapset = await client.get_beatmapset(score.beatmap.beatmapset_id)
                for score in self.scores:
                    score.beatmapset = beatmapset

            self.set_thumbnail(url=score.beatmapset.covers.list)

            self.difficulty_attrs = [
                await client.get_beatmap_attributes(
                    score.beatmap.id,
                    mods=score.mods,
                    mode=score.mode,
                ),
            ] * len(self.scores)

        if len(self.difficulty_attrs) != len(self.scores):
            for score in self.scores:
                self.difficulty_attrs.append(
                    await client.get_beatmap_attributes(
                        score.beatmap.id,
                        mods=score.mods,
                        mode=score.mode,
                    ),
                )

        for idx, score in enumerate(self.scores):
            data = _score_to_embed_strs(score, False, self.difficulty_attrs[idx])
            if self.same_beatmap:
                data["name"] = "_ _"

            self.add_field(inline=False, **data)
        self.prepared = True
