###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from datetime import timedelta
from inspect import cleandoc
from typing import TYPE_CHECKING

from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from aiosu.models import BeatmapDifficultyAttributes
    from aiosu.models import Beatmap
    from aiosu.models import Mods
    from discord import commands


class OsuDifficultyEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        beatmap: Beatmap,
        difficulty_attributes: BeatmapDifficultyAttributes,
        mods: Mods,
    ):
        beatmapset = beatmap.beatmapset
        mods_text = f" +{mods}" if int(mods) > 0 else ""
        super().__init__(
            ctx,
        )

        self.set_author(
            name=f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]{mods_text}",
            url=beatmap.url,
        )

        self.set_thumbnail(url=beatmap.beatmapset.covers.list_2_x)

        difficulty_attributes_dict = difficulty_attributes.dict(exclude_none=True)

        total_length = timedelta(seconds=beatmap.total_length)
        drain_time = timedelta(seconds=beatmap.hit_length)
        max_combo = difficulty_attributes_dict.pop("max_combo")

        beatmap_content = cleandoc(
            f"""
            **{total_length}** total length
            **{drain_time}** drain time
            **{beatmap.bpm}** bpm
            **{max_combo}** max combo
            **{beatmap.count_circles}** circles
            **{beatmap.count_sliders}** sliders
            **{beatmap.count_spinners}** spinners
            """,
        )

        self.add_field(name="Beatmap Attributes", value=beatmap_content)

        difficulty_content = ""
        for key, value in difficulty_attributes_dict.items():
            difficulty_content += f"**{value:.2f}** {key.replace('_', ' ')}\n"

        self.add_field(name="Difficulty Attributes", value=difficulty_content)
