###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from common.humanizer import milliseconds_to_duration
from pomice import Playlist
from pomice import Track
from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from discord import commands


class MusicTrackEmbed(ContextEmbed):
    def __init__(
        self,
        ctx: commands.Context,
        track: Track,
        title="Now playing",
        position=0,
    ):
        self.track = track
        self.title_str = (
            f"**{track.title}** by **{track.author}**"
            if track.author
            else f"{track.title}"
        )
        live_str = ":red_circle: **LIVE** " if track.is_stream else ""
        description = f"{live_str}[{self.title_str}]({track.uri})"

        super().__init__(
            ctx,
            title=title,
            description=description,
        )

        position_text = ""
        if position:
            position_text += f"Position: {milliseconds_to_duration(track.position)} | "

        self.set_author(name=f"Requested by {track.requester}")
        self.set_footer(
            text=f"{position_text}Length: {milliseconds_to_duration(track.length)}",
        )
        self.set_thumbnail(url=track.thumbnail)


class MusicPlaylistEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, playlist: Playlist):
        self.playlist = playlist
        super().__init__(
            ctx,
            title=f"Playlist {playlist.name}",
            description=f"Added **{playlist.track_count}** songs to the queue!",
        )
        self.set_thumbnail(url=playlist.thumbnail)
