from __future__ import annotations

import classes.osu as osu
import discord


class OsuRecentEmbed(discord.Embed):
    def __init__(self, score: osu.Score, beatmap: osu.Beatmap, color: str):
        if score.performance.completion != 100:
            score.rank = osu.Rank.F  # Weird non-bancho API behaviour

        description = (
            f"""
> {score.rank.icon} > **{score.performance.pp:.2f}PP"""
            + (
                f"({score.performance.pp_fc:.2f}PP for {score.performance.accuracy_fc:.2f}% FC)"
                if not score.perfect and score.mode != osu.Mode.MANIA
                else ""
            )
            + f"""** > {score.performance.accuracy:.2f}%
> {score.score} > x{score.maxcombo}/{beatmap.max_combo} > [{score.count300}/{score.count100}/{score.count50}/{score.countmiss}]"""
        )

        if score.performance.completion != 100:
            description += f"""
> **Completion:** {score.performance.completion:.2f}%"""

        super().__init__(
            title=None,
            color=color,
            description=description,
            timestamp=score.date,
        )

        self.set_author(
            name=f"{beatmap.title} [{beatmap.version}] ({beatmap.creator}) +{str(score.enabled_mods)} [{score.performance.star_rating:.2f}★]",
            url=score.server.url_beatmap + str(beatmap.beatmap_id),
            icon_url=score.server.url_avatar + str(score.user_id),
        )
        self.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap.beatmapset_id}.jpg")
        self.set_footer(
            text=f"{beatmap.status.name.lower()} | osu! {score.mode.name_full} Play",
            icon_url=score.mode.icon,
        )
