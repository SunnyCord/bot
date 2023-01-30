from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from aiosu.models import Gamemode
from aiosu.models import User
from discord.ext import commands
from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from typing import Any


def seconds_to_text(secs: int) -> str:
    result = "0 seconds"
    if secs > 0:
        days = secs // 86400
        hours = (secs - days * 86400) // 3600
        minutes = (secs - days * 86400 - hours * 3600) // 60
        seconds = secs - days * 86400 - hours * 3600 - minutes * 60
        result = (
            ("{} day{} ".format(days, "s" if days != 1 else "") if days else "")
            + ("{} hour{} ".format(hours, "s" if hours != 1 else "") if hours else "")
            + (
                "{} minute{} ".format(minutes, "s" if minutes != 1 else "")
                if minutes
                else ""
            )
            + (
                "{} second{} ".format(seconds, "s" if seconds != 1 else "")
                if seconds
                else ""
            )
        )
    return result


class OsuProfileEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        user: User,
        mode: Gamemode,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            ctx,
            title=None,
            description=f"""
            > **Rank:** #{user.statistics.global_rank}
            > **PP:** {user.statistics.pp}
            > **Accuracy:** {user.statistics.hit_accuracy:.2f}%
            > **Level:** {user.statistics.level.current} ({user.statistics.level.progress:.2f}%)
            > **Playtime:** {seconds_to_text(user.statistics.play_time)}
            > **Playcount:** {user.statistics.play_count}
            > **PP/hour:** {int(user.statistics.pp / user.statistics.play_time * 3600)  if user.statistics.play_time > 0 else 0}
            """,
            timestamp=datetime.utcnow(),
            *args,
            **kwargs,
        )
        self.set_author(
            name=f"osu! {mode.name_full} stats for {user.username}",
            url=user.url,
            icon_url=mode.icon,
        )
        self.set_thumbnail(url=user.avatar_url)
        self.set_footer(
            text=f"#{user.statistics.country_rank}",
            icon_url=f"https://osu.ppy.sh/images/flags/{user.country_code}.png",
        )
