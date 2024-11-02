###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from inspect import cleandoc
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


class OsuProfileCompactEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        user: User,
        mode: Gamemode,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        peak_str = ""
        if user.rank_highest:
            peak_str = f"(peaked #{user.rank_highest.rank} {format_dt(user.rank_highest.updated_at)}\n"

        if user.rank_history:
            peak_str += f"avg. ranks/day: {user.rank_history.average_gain:.2f} | "

        content = (
            f"{user.statistics.pp}pp (#{user.statistics.global_rank} | {user.country.flag_emoji}#{user.statistics.country_rank})\n"
            + peak_str
            + cleandoc(
                f"""
                pp/hour: {user.statistics.pp_per_playtime:.2f}
                accuracy: {user.statistics.hit_accuracy:.2f}%
                level: {user.statistics.level.current} ({user.statistics.level.progress:.2f}%)
                """,
            )
        )

        safe_username = escape_markdown(user.username)
        online_str = "🟢" if user.is_online else "🔴"

        super().__init__(
            ctx,
            title=None,
            description=content,
            *args,
            **kwargs,
        )
        self.set_author(
            name=f"osu! {mode.name_full} stats for {safe_username} {online_str}",
            url=user.url,
            icon_url=GamemodeIcon[mode.name].icon,
        )
        self.set_thumbnail(url=user.avatar_url)


class OsuProfileExtendedEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        user: User,
        mode: Gamemode,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        peak_str = ""
        if user.rank_highest:
            peak_str = f"peak: **#{user.rank_highest.rank}** {format_dt(user.rank_highest.updated_at)}\n"

        rank_content = (
            f"rank: **#{user.statistics.global_rank}**\n"
            + peak_str
            + cleandoc(
                f"""
                country rank: **{user.country.flag_emoji}#{user.statistics.country_rank}**
                pp: **{user.statistics.pp}**
                acc: **{user.statistics.hit_accuracy:.2f}%**
                level: **{user.statistics.level.current}** (**{user.statistics.level.progress:.2f}%**)
                """,
            )
        )
        self.add_field(name="", value=rank_content)

        rank_gain_str = ""
        if user.rank_history:
            rank_gain_str = (
                f"\navg. rank gain: **{user.rank_history.average_gain:.2f}**\n"
            )

        average_content = cleandoc(
            f"""
            max combo: **{user.statistics.maximum_combo}**
            pp/hour: **{user.statistics.pp_per_playtime:.2f}**{rank_gain_str}
            joined: {format_dt(user.join_date)}
            """,
        )
        self.add_field(name="", value=average_content)

        self.add_field(name="", value="", inline=False)

        play_content = cleandoc(
            f"""
            playtime: **{humanizer.seconds_to_text(user.statistics.play_time)}**
            playcount: **{humanizer.number(user.statistics.play_count)}**
            total score: **{humanizer.number(user.statistics.total_score)}**
            ranked score: **{humanizer.number(user.statistics.ranked_score)}**
            total hits: **{humanizer.number(user.statistics.total_hits)}**
            """,
        )
        self.add_field(name="", value=play_content)

        playstyle_str = ""
        if user.playstyle:
            playstyle_str = f"playstyle: **{' '.join(user.playstyle)}**\n"
        playstyle_content = cleandoc(
            f"""
            {playstyle_str}followers: **{user.follower_count}**
            has supported: **{user.has_supported}**
            support level: **{user.support_level}**
            total kudosu: **{humanizer.number(user.kudosu.total)}**
            """,
        )
        self.add_field(name="", value=playstyle_content)

        safe_username = escape_markdown(user.username)
        online_str = "🟢" if user.is_online else "🔴"

        super().__init__(
            ctx,
            title=None,
            *args,
            **kwargs,
        )
        self.set_author(
            name=f"osu! {mode.name_full} stats for {safe_username} {online_str}",
            url=user.url,
            icon_url=GamemodeIcon[mode.name].icon,
        )
        self.set_thumbnail(url=user.avatar_url)
