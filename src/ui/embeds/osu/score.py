###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from inspect import cleandoc
from typing import TYPE_CHECKING

from aiosu.models import BeatmapRankStatus
from aiosu.models import LazerScore
from aiosu.models import Mod
from aiosu.models import Score
from aiosu.utils.performance import get_calculator
from discord.utils import escape_markdown
from ui.embeds.generic import ContextEmbed
from ui.icons.score import ScoreRankIcon

if TYPE_CHECKING:
    from typing import Any
    import aiosu
    from discord import commands


def _check_leaderboarded(score: aiosu.models.Score) -> bool:
    return score.beatmap.status in (
        BeatmapRankStatus.APPROVED,
        BeatmapRankStatus.QUALIFIED,
        BeatmapRankStatus.LOVED,
        BeatmapRankStatus.RANKED,
    )


async def get_score_beatmap_attributes(
    score: aiosu.models.Score,
    client: aiosu.v2.Client,
) -> aiosu.models.BeatmapDifficultyAttributes | None:
    if not _check_leaderboarded(score):
        return None

    return await client.get_beatmap_attributes(
        score.beatmap.id,
        mods=score.mods,
        mode=score.mode,
    )


def _get_lazer_speed_modifier(mod):
    speed_change = mod.settings.get("speed_change")
    if speed_change:
        return float(speed_change)
    elif mod.acronym in ["DT", "NC"]:
        return 1.5
    elif mod.acronym in ["HT", "DC"]:
        return 0.75
    else:
        return 1.0


def _get_score_bpm(score: aiosu.models.Score) -> str:
    speed_modifier = 1.0

    if isinstance(score, LazerScore):
        for mod in score.mods:
            speed_modifier = _get_lazer_speed_modifier(mod)
            if speed_modifier != 1.0:
                break
    else:
        if score.mods & (Mod.DoubleTime | Mod.Nightcore):
            speed_modifier = 1.5
        elif score.mods & Mod.HalfTime:
            speed_modifier = 0.75

    return f"{score.beatmap.bpm * speed_modifier:.0f}" if score.beatmap.bpm else "?"


def _score_to_embed_strs(
    score: Score,
    include_user: bool = False,
    difficulty_attrs: aiosu.models.BeatmapDifficultyAttributes | None = None,
) -> dict[str, str]:
    beatmap, beatmapset = score.beatmap, score.beatmapset

    name = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"

    statistics = score.statistics
    max_combo = beatmap.max_combo
    pp = score.pp or 0.0
    pp_fc = None

    if difficulty_attrs:
        name += f" ({difficulty_attrs.star_rating:.2f}★)"
        max_combo = difficulty_attrs.max_combo
        calculator_type = get_calculator(score.mode)
        calculator = calculator_type(difficulty_attrs)

        if not pp:
            pp = calculator.calculate(score).total

        if hasattr(calculator, "_calculate_effective_miss_count"):
            is_fc = True
            if score.passed:
                is_fc = calculator._calculate_effective_miss_count(score) == 0
            if not is_fc or not score.passed:
                score_fc = score.model_copy()
                score_fc.statistics = score.statistics.model_copy()
                score_fc.max_combo = max_combo
                adjusted_greats = (
                    beatmap.count_objects
                    - score.statistics.count_100
                    - score.statistics.count_50
                )
                if isinstance(score, LazerScore):
                    score_fc.statistics.great = adjusted_greats
                    score_fc.statistics.miss = 0
                else:
                    score_fc.statistics.count_300 = adjusted_greats
                    score_fc.statistics.count_miss = 0
                pp_fc = calculator.calculate(score_fc).total

    if beatmapset.creator:
        name += f" <{beatmapset.creator}>"

    weight = "" if not score.weight else f" (weight {score.weight.percentage/100:.2f})"
    score_text = f"[score]({score.score_url}) | " if score.score_url else ""
    user_text = f"[user]({score.user.url}) | " if include_user else ""
    fc_text = "" if not pp_fc else f"(FC: **{pp_fc:.2f}pp**) "

    fail_text = "" if score.passed else f" ({score.completion:.2f}%)"
    bpm_text = _get_score_bpm(score)

    mods_text = score.mods
    mods_settings_text = ""
    if isinstance(score, LazerScore):
        mods_text = score.mods_str
        mods_settings_text = "\n"
        for mod in score.mods:
            for key, value in mod.settings.items():
                mods_settings_text += f"{key.replace('_', ' ')}: {value}\n"
        mods_settings_text = mods_settings_text.rstrip()

    value = cleandoc(
        f"""**{pp:.2f}pp**{weight}, accuracy: **{score.accuracy*100:.2f}%**, combo: **{score.max_combo}x/{max_combo}x**
            {fc_text}score: **{score.score}** [**{statistics.count_300}**/**{statistics.count_100}**/**{statistics.count_50}**/**{statistics.count_miss}**]
            bpm: {bpm_text} | mods: {mods_text} | {ScoreRankIcon[score.rank]}{fail_text}{mods_settings_text}
            <t:{score.created_at.timestamp():.0f}:R>
            {score_text}{user_text}[map]({beatmap.url})
        """,
    )
    return {
        "name": escape_markdown(name),
        "value": value,
    }


class OsuScoreSingleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        score: Score,
        title: str = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, *args, **kwargs)
        self.ctx = ctx
        self.prepared = False
        self.score = score

        safe_username = escape_markdown(score.user.username)

        self.set_thumbnail(url=self.score.beatmapset.covers.list)
        self.set_author(
            name=title or safe_username,
            icon_url=self.score.user.avatar_url,
        )

    async def prepare(self) -> None:
        if self.prepared:
            return

        client = await self.ctx.bot.stable_storage.app_client

        difficulty_attrs = await get_score_beatmap_attributes(self.score, client)

        self.add_field(
            inline=False,
            **_score_to_embed_strs(self.score, True, difficulty_attrs),
        )

        self.prepared = True


class OsuScoreMultipleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        scores: list[Score],
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

        client = await self.ctx.bot.stable_storage.app_client

        if self.same_beatmap:
            score = self.scores[0]
            if not score.beatmapset:
                beatmapset = await client.get_beatmapset(score.beatmap.beatmapset_id)
                for score in self.scores:
                    score.beatmapset = beatmapset

            self.set_thumbnail(url=score.beatmapset.covers.list)

            self.difficulty_attrs = [
                await get_score_beatmap_attributes(score, client),
            ] * len(self.scores)

        else:
            for score in self.scores:
                self.difficulty_attrs.append(
                    await get_score_beatmap_attributes(score, client),
                )

        for idx, score in enumerate(self.scores):
            data = _score_to_embed_strs(score, False, self.difficulty_attrs[idx])
            if self.same_beatmap:
                data["name"] = "_ _"

            self.add_field(inline=False, **data)
        self.prepared = True
