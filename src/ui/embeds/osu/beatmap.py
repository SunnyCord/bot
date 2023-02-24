from __future__ import annotations

from datetime import timedelta
from inspect import cleandoc
from typing import TYPE_CHECKING

from aiosu.models import Beatmap
from aiosu.models import Beatmapset
from ui.embeds.generic import ContextEmbed
from ui.icons.beatmap import BeatmapDifficultyIcon

if TYPE_CHECKING:
    from typing import Any
    from discord.ext.commands import Context


class OsuBeatmapEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: Context,
        beatmapset: Beatmapset,
        beatmap: Beatmap,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.beatmapset = beatmapset
        self.beatmap = beatmap

        footer_date_prefix = "Last updated "
        date = beatmapset.last_updated
        if beatmapset.ranked_date:
            footer_date_prefix = "Approved "
            date = beatmapset.ranked_date

        title = f"{beatmapset.artist} - {beatmapset.title}"
        description = cleandoc(
            f"""**Length**: {timedelta(seconds=beatmap.total_length)} **BPM:** {beatmap.bpm}\n**Download:** [map](https://osu.ppy.sh/d/{beatmapset.id})([🚫📹](https://osu.ppy.sh/d/{beatmapset.id}n)) [chimu.moe](https://api.chimu.moe/v1/download/{beatmapset.id})
                **Discussion:** [mapset]({beatmapset.discussion_url}) [difficulty]({beatmap.discussion_url})
                [**Browser Preview**](https://osu-preview.jmir.ml/preview#{beatmap.id})
            """,
        )

        super().__init__(
            ctx,
            title=title,
            description=description,
            url=beatmap.url,
            *args,
            **kwargs,
        )

        self.set_author(
            name=f"Mapped by {beatmapset.creator}",
            icon_url=f"https://a.ppy.sh/{beatmapset.user_id}",
            url=f"https://osu.ppy.sh/users/{beatmapset.user_id}/modding",
        )

        self.set_thumbnail(url=beatmapset.covers.list)

        content = cleandoc(
            f"""**▸** {beatmap.difficulty_rating:.2f}⭐  **▸Max Combo:** x{beatmap.max_combo}\n**▸AR:** {beatmap.ar}  **▸OD:** {beatmap.accuracy}  **▸CS:** {beatmap.cs}  **▸HP:** {beatmap.drain}
                {beatmap.status.name} | ❤️ {beatmapset.favourite_count} | ▶️ {beatmapset.play_count}
                {footer_date_prefix}<t:{date.timestamp():.0f}:R>
            """,
        )

        self.add_field(
            name=f"{BeatmapDifficultyIcon.get_from_sr(beatmap.difficulty_rating, beatmap.mode)}__{beatmap.version}__",
            value=content,
        )
