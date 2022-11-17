from __future__ import annotations

import classes.osu as osu
import discord


class OsuPerformanceEmbed(discord.Embed):
    def __init__(self, beatmap: osu.Beatmap, perf_info: dict, color: str):
        super().__init__(
            title=f"{beatmap.title} [{beatmap.version}] ({beatmap.creator}) [{perf_info.star_rating:.2f}★] +{str(perf_info.mods)}",
            url=beatmap.beatmap_url,
            color=color,
        )

        self.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap.beatmapset_id}.jpg")
        self.add_field(name="100%", value=f"{perf_info.pp_100:.2f}pp")
        self.add_field(name="99%", value=f"{perf_info.pp_99:.2f}pp")
        self.add_field(name="97%", value=f"{perf_info.pp_97:.2f}pp")
        self.add_field(name="95%", value=f"{perf_info.pp_95:.2f}pp")

        self.set_footer(text="plz enjoy game")
