###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from common.humanizer import milliseconds_to_duration
from pomice import Track
from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from discord import commands


class MusicTrackEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, track: Track, title="Now playing"):
        live_str = ":red_circle: **LIVE** " if track.is_stream else ""
        description = f"{live_str}[{track.title}]({track.uri})"
        super().__init__(
            ctx,
            title=title,
            description=description,
        )
        self.set_author(name=f"Requested by {track.requester}")
        self.set_footer(text=f"Length: {milliseconds_to_duration(track.length)}")
        self.set_thumbnail(url=track.thumbnail)


class MusicPlaylistEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, playlist: list[Track]):
        super().__init__(
            ctx,
            title="Playlist",
            description=f"Added {len(playlist)} songs to the queue!",
        )
        self.set_thumbnail(url=ctx.bot.user.avatar)
