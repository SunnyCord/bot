###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from aiosu.models import BeatmapDifficultyAttributes
from aiosu.models import BeatmapRankStatus
from aiosu.models import Gamemode
from aiosu.models import OsuPerformanceAttributes
from aiosu.models import Score
from aiosu.utils.accuracy import get_calculator as get_accuracy_calculator
from aiosu.utils.performance import get_calculator
from discord.utils import escape_markdown
from discord.utils import format_dt

from ui.embeds.generic import ContextEmbed
from ui.icons.score import ScoreRankIcon

if TYPE_CHECKING:
    from typing import Any

    from aiosu.v2 import Client
    from discord.ext.commands import Context


async def get_score_beatmap_attributes(
    score: Score,
    client: Client,
) -> BeatmapDifficultyAttributes | None:
    if score.beatmap is None or score.beatmap.status not in (
        BeatmapRankStatus.APPROVED,
        BeatmapRankStatus.QUALIFIED,
        BeatmapRankStatus.LOVED,
        BeatmapRankStatus.RANKED,
    ):
        return None
    return await client.get_beatmap_attributes(
        score.beatmap.id,
        mods=score.mods,
        mode=score.mode,
    )


def _get_score_bpm(score: Score) -> str:
    if score.beatmap is None or not score.beatmap.bpm:
        return "?"
    speed = 1.0
    for mod in score.mods:
        if mod.acronym == "DT" and "NC" in score.mods and not mod.settings:
            continue
        if mod.acronym in ("DT", "NC", "HT", "DC"):
            default = 1.5 if mod.acronym in ("DT", "NC") else 0.75
            speed *= float(mod.settings.get("speed_change", default))
        elif mod.acronym in ("WU", "WD", "AS"):
            speed *= float(mod.settings.get("initial_rate", 1.0))
    return f"{score.beatmap.bpm * speed:.0f}"


def _score_performance(
    score: Score,
    attributes: BeatmapDifficultyAttributes | None,
) -> tuple[float, float | None]:
    pp = score.pp or 0.0
    if attributes is None or score.beatmap is None:
        return pp, None
    calculator = get_calculator(score.mode)(attributes)
    try:
        performance = calculator.calculate(score)
    except ValueError:
        return pp, None
    pp = pp or performance.total
    if score.mode != Gamemode.STANDARD:
        return pp, None
    if (
        not isinstance(performance, OsuPerformanceAttributes)
        or score.beatmap.count_objects is None
    ):
        return pp, None
    if score.passed and performance.effective_miss_count == 0:
        return pp, None
    full_combo = score.model_copy(deep=True)
    full_combo.max_combo = attributes.max_combo
    full_combo.passed = True
    full_combo.legacy_total_score = None
    full_combo.statistics.great = max(
        0,
        score.beatmap.count_objects - score.statistics.ok - score.statistics.meh,
    )
    full_combo.statistics.miss = 0
    full_combo.statistics.large_tick_miss = 0
    full_combo.statistics.slider_tail_hit = score.beatmap.count_sliders
    full_combo.accuracy = get_accuracy_calculator(score.mode).calculate(full_combo)
    try:
        return pp, calculator.calculate(full_combo).total
    except ValueError:
        return pp, None


def _score_hits(score: Score) -> str:
    statistics = score.statistics
    counts = [statistics.count_300, statistics.count_100]
    if score.mode != Gamemode.TAIKO:
        counts.append(statistics.count_50)
    if score.mode == Gamemode.MANIA:
        counts.insert(0, statistics.count_geki)
        counts.append(statistics.count_katu)
    elif score.mode == Gamemode.CTB:
        counts.append(statistics.count_katu)
    counts.append(statistics.count_miss)
    return "/".join(f"**{count}**" for count in counts)


def _score_to_embed_strs(
    score: Score,
    include_user: bool = False,
    difficulty_attrs: BeatmapDifficultyAttributes | None = None,
) -> dict[str, str]:
    beatmap = score.beatmap
    beatmapset = score.beatmapset or (beatmap.beatmapset if beatmap else None)
    if beatmap is None or beatmapset is None:
        raise ValueError("Score is missing beatmap details.")
    name = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"
    if difficulty_attrs:
        name += f" ({difficulty_attrs.star_rating:.2f}★)"
    if beatmapset.creator:
        name += f" <{beatmapset.creator}>"
    max_combo = difficulty_attrs.max_combo if difficulty_attrs else beatmap.max_combo
    pp, pp_fc = _score_performance(score, difficulty_attrs)
    weight = f" (weight {score.weight.percentage / 100:.2f})" if score.weight else ""
    fc = f"(FC: **{pp_fc:.2f}pp**) " if pp_fc is not None else ""
    fail = ""
    if not score.passed and score.completion is not None:
        fail = f" ({score.completion:.2f}%)"
    links = []
    if score.score_url:
        links.append(f"[score]({score.score_url})")
    if include_user and score.user:
        links.append(f"[user]({score.user.url})")
    links.append(f"[map]({beatmap.url})")
    lines = [
        f"**{pp:.2f}pp**{weight}, accuracy: **{score.accuracy * 100:.2f}%**, combo: **{score.max_combo}x/{max_combo or '?'}x**",
        f"{fc}score: **{score.score}** [{_score_hits(score)}]",
        f"bpm: {_get_score_bpm(score)} | mods: {score.mods} | {ScoreRankIcon[score.rank]}{fail}",
    ]
    lines.extend(
        f"{mod.acronym} {key.replace('_', ' ')}: {value}"
        for mod in score.mods
        for key, value in mod.settings.items()
    )
    lines.extend((format_dt(score.created_at, style="R"), " | ".join(links)))
    return {"name": escape_markdown(name), "value": "\n".join(lines)}


class OsuScoreSingleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: Context,
        score: Score,
        title: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, *args, **kwargs)
        self.ctx = ctx
        self.prepared = False
        self.score = score
        beatmapset = score.beatmapset or (
            score.beatmap.beatmapset if score.beatmap else None
        )
        if beatmapset:
            self.set_thumbnail(url=beatmapset.covers.list)
        if score.user:
            self.set_author(
                name=title or escape_markdown(score.user.username),
                icon_url=score.user.avatar_url,
            )
        elif title:
            self.set_author(name=title)

    async def prepare(self) -> None:
        if self.prepared:
            return
        client = await self.ctx.bot.client_storage.app_client
        attributes = await get_score_beatmap_attributes(self.score, client)
        self.add_field(
            inline=False,
            **_score_to_embed_strs(self.score, True, attributes),
        )
        self.prepared = True


class OsuScoreMultipleEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: Context,
        scores: list[Score],
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
        if self.prepared or not self.scores:
            return
        client = await self.ctx.bot.client_storage.app_client
        if self.same_beatmap:
            first = self.scores[0]
            if first.beatmap is None:
                raise ValueError("Score is missing beatmap details.")
            beatmapset = first.beatmapset or first.beatmap.beatmapset
            if beatmapset is None:
                beatmapset = await client.get_beatmapset(first.beatmap.beatmapset_id)
            for score in self.scores:
                score.beatmapset = beatmapset
            self.set_thumbnail(url=beatmapset.covers.list)
        for score in self.scores:
            attributes = await get_score_beatmap_attributes(score, client)
            data = _score_to_embed_strs(score, difficulty_attrs=attributes)
            if self.same_beatmap:
                data["name"] = "_ _"
            self.add_field(inline=False, **data)
        self.prepared = True
