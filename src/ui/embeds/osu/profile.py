###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from aiosu.models import Gamemode
from aiosu.models import User
from discord.ext import commands
from discord.utils import escape_markdown
from discord.utils import format_dt

from common import humanizer
from ui.embeds.generic import ContextEmbed
from ui.icons import GamemodeIcon

if TYPE_CHECKING:
    from typing import Any


class _OsuProfileEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        user: User,
        mode: Gamemode,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, *args, **kwargs)
        online = "🟢" if user.is_online else "🔴"
        self.set_author(
            name=f"osu! {mode.name_full} stats for {escape_markdown(user.username)} {online}",
            url=user.url,
            icon_url=GamemodeIcon[mode.name].icon,
        )
        self.set_thumbnail(url=user.avatar_url)


class OsuProfileCompactEmbed(_OsuProfileEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        user: User,
        mode: Gamemode,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, user, mode, *args, **kwargs)
        stats = user.statistics
        if stats is None or stats.level is None:
            self.description = "No statistics available."
            return
        country = user.country.flag_emoji if user.country else user.country_code
        lines = [
            f"{stats.pp}pp (#{stats.global_rank} | {country}#{stats.country_rank})",
        ]
        if user.rank_highest:
            peak = user.rank_highest
            lines.append(f"peaked #{peak.rank} {format_dt(peak.updated_at)}")
        if user.rank_history:
            lines.append(f"avg. ranks/day: {user.rank_history.average_gain:.2f}")
        lines.extend(
            (
                f"pp/hour: {stats.pp_per_playtime:.2f}",
                f"accuracy: {stats.hit_accuracy:.2f}%",
                f"level: {stats.level.current} ({stats.level.progress:.2f}%)",
            ),
        )
        self.description = "\n".join(lines)


class OsuProfileExtendedEmbed(_OsuProfileEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        user: User,
        mode: Gamemode,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, user, mode, *args, **kwargs)
        stats = user.statistics
        if stats is None or stats.level is None:
            self.description = "No statistics available."
            return
        country = user.country.flag_emoji if user.country else user.country_code
        ranks = [f"rank: **#{stats.global_rank}**"]
        if user.rank_highest:
            peak = user.rank_highest
            ranks.append(f"peak: **#{peak.rank}** {format_dt(peak.updated_at)}")
        ranks.extend(
            (
                f"country rank: **{country}#{stats.country_rank}**",
                f"pp: **{stats.pp}**",
                f"acc: **{stats.hit_accuracy:.2f}%**",
                f"level: **{stats.level.current}** (**{stats.level.progress:.2f}%**)",
            ),
        )
        averages = [
            f"max combo: **{stats.maximum_combo}**",
            f"pp/hour: **{stats.pp_per_playtime:.2f}**",
            f"joined: {format_dt(user.join_date)}",
        ]
        if user.rank_history:
            averages.append(f"avg. rank gain: **{user.rank_history.average_gain:.2f}**")
        play = [
            f"playtime: **{humanizer.seconds_to_text(stats.play_time or 0)}**",
            f"playcount: **{humanizer.number(stats.play_count or 0)}**",
            f"total score: **{humanizer.number(stats.total_score or 0)}**",
            f"ranked score: **{humanizer.number(stats.ranked_score or 0)}**",
            f"total hits: **{humanizer.number(stats.total_hits or 0)}**",
        ]
        profile = [
            f"followers: **{user.follower_count}**",
            f"has supported: **{user.has_supported}**",
            f"support level: **{user.support_level}**",
            f"total kudosu: **{humanizer.number(user.kudosu.total)}**",
        ]
        if user.playstyle:
            profile.insert(0, f"playstyle: **{' '.join(user.playstyle)}**")
        for name, lines in (
            ("Ranks", ranks),
            ("Averages", averages),
            ("Play", play),
            ("Profile", profile),
        ):
            self.add_field(name=name, value="\n".join(lines))
