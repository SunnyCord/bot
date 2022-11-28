from __future__ import annotations

from datetime import datetime

import classes.osu as osu
import discord


class OsuProfileEmbed(discord.Embed):
    @classmethod
    def __secondsToText(cls, secs):
        result = "0 seconds"
        if secs > 0:
            days = secs // 86400
            hours = (secs - days * 86400) // 3600
            minutes = (secs - days * 86400 - hours * 3600) // 60
            seconds = secs - days * 86400 - hours * 3600 - minutes * 60
            result = (
                ("{} day{} ".format(days, "s" if days != 1 else "") if days else "")
                + (
                    "{} hour{} ".format(hours, "s" if hours != 1 else "")
                    if hours
                    else ""
                )
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

    def __init__(self, user: osu.User, mode: osu.Mode, color: str):
        super().__init__(
            title=None,
            color=color,
            description=f"> **Rank:** #{user.pp_rank}\n\
> **PP:** {user.pp_raw}\n\
> **Accuracy:** {user.accuracy:.2f}%\n\
> **Level:** {int(user.level)} ({user.level_progress:.2f}%)\n\
> **Playtime:** {self.__secondsToText(user.total_seconds_played)}\n\
> **Playcount:** {user.playcount}\n\
> **PP/hour:** {int(user.pp_raw/user.total_seconds_played*3600) if user.total_seconds_played > 0 else 0}",
            timestamp=datetime.utcnow(),
        )
        self.set_author(
            name=f"osu! {mode.name_full} stats for {user.username} on {user.server.name_full}",
            url=user.profile_url,
            icon_url=mode.icon,
        )
        self.set_thumbnail(url=user.avatar_url)
        self.set_footer(
            text=f"#{user.pp_country_rank}",
            icon_url=f"https://osu.ppy.sh/images/flags/{user.country}.png",
        )
