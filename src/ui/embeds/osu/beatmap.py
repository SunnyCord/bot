from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from aiosu.classes import Beatmapset
from discord import Embed
from ui.emojis.beatmap import BeatmapDifficultyIcon

if TYPE_CHECKING:
    from typing import Any


def get_diff_icon(sr: float, mode_id: int) -> BeatmapDifficultyIcon:
    if sr < 2:
        return BeatmapDifficultyIcon[f"EASY_{mode_id}"]
    if sr < 2.7:
        return BeatmapDifficultyIcon[f"NORMAL_{mode_id}"]
    if sr < 4:
        return BeatmapDifficultyIcon[f"HARD_{mode_id}"]
    if sr < 5.3:
        return BeatmapDifficultyIcon[f"INSANE_{mode_id}"]
    if sr < 6.5:
        return BeatmapDifficultyIcon[f"EXTRA_{mode_id}"]
    return BeatmapDifficultyIcon[f"EXPERT_{mode_id}"]


class OsuBeatmapEmbed(Embed):
    def __init__(self, beatmapset: Beatmapset, *args: Any, **kwargs: Any) -> None:
        beatmap = beatmapset.beatmaps[0]
        footer_date_prefix = "Last updated"
        date = beatmapset.last_updated
        if beatmapset.ranked_date:
            footer_date_prefix = "Approved"
            date = beatmapset.ranked_date
        super().__init__(
            title=f"{beatmapset.artist} - {beatmapset.title}",
            description=f"""**Length**: {timedelta(seconds=beatmap.total_length)} **BPM:** {beatmap.bpm}\n**Download:** [map](https://osu.ppy.sh/d/{beatmapset.id})([🚫📹](https://osu.ppy.sh/d/{beatmapset.id}n)) [chimu.moe](https://api.chimu.moe/v1/download/{beatmapset.id})
                        **Discussion:** [mapset]({beatmapset.discussion_url}) [difficulty]({beatmap.discussion_url})
                        [**Browser Preview**](https://osu-preview.jmir.ml/preview#{beatmap.id})
                        """,
            url=beatmap.url,
            timestamp=date,
            *args,
            **kwargs,
        )
        self.set_author(
            name=f"Mapped by {beatmapset.creator}",
            icon_url=f"https://a.ppy.sh/{beatmapset.user_id}",
            url=f"https://osu.ppy.sh/users/{beatmapset.user_id}/modding",
        )
        self.set_thumbnail(url=beatmapset.covers.list)
        self.set_footer(
            text=f"{beatmap.status.name} | ❤️ {beatmapset.favourite_count} | ▶️ {beatmapset.play_count} | {footer_date_prefix}",
        )
        self.add_field(
            name=f"{get_diff_icon(beatmap.difficulty_rating, beatmap.mode.id).value}__{beatmap.version}__",
            value=f"**▸** {beatmap.difficulty_rating:.2f}⭐  **▸Max Combo:** x{beatmap.max_combo}\n**▸AR:** {beatmap.ar}  **▸OD:** {beatmap.accuracy}  **▸CS:** {beatmap.cs}  **▸HP:** {beatmap.drain}",
        )
