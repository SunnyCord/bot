###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from contextlib import suppress
from typing import Any

import pomice
from discord import HTTPException
from discord import Member
from discord import Message
from discord.ext.commands import Context
from models.guild_settings import GuildSettings
from ui.embeds.music import MusicTrackEmbed


class Player(pomice.Player):
    """Pomice guild player."""

    __slots__ = (
        "queue",
        "controller",
        "context",
        "guild_settings",
        "dj",
        "auto_play",
        "loop_mode",
        "pause_votes",
        "resume_votes",
        "skip_votes",
        "shuffle_votes",
        "stop_votes",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.queue: pomice.Queue = pomice.Queue()
        self.controller: Message | None = None
        self.context: Context | None = None
        self.guild_settings: GuildSettings | None = None
        self.dj: Member | None = None
        self.auto_play: bool = False

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()

    def disable_loop(self) -> None:
        if self.queue.is_looping:
            self.queue.disable_loop()
            return

    def in_queue(self, track: pomice.Track) -> bool:
        is_in_queue = track in self.queue
        is_playing = self.current and self.current.uri == track.uri
        return is_in_queue or is_playing

    async def do_next(self) -> None:
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        if self.controller:
            with suppress(HTTPException):
                await self.controller.delete()

        track = None
        try:
            track = self.queue.get()
        except pomice.QueueEmpty:
            should_disconnect = self.guild_settings.voice_auto_disconnect

            if self.auto_play:
                recommendations = await self.get_recommendations(
                    track=self._ending_track,
                    ctx=self.context,
                )

                next_track = None
                if recommendations:
                    next_track = next(
                        (
                            track
                            for track in recommendations
                            if track.uri != self._ending_track.uri
                        ),
                        None,
                    )

                if next_track:
                    should_disconnect = False
                    track = next_track

            if should_disconnect:
                await self.teardown()
                return

            if not track:
                return

        await self.play(track)

        self.controller = await self.context.send(
            embed=MusicTrackEmbed(self.context, track),
        )

    async def teardown(self) -> None:
        with suppress(HTTPException, KeyError):
            await self.destroy()
            if self.controller:
                await self.controller.delete()

    async def set_context(self, ctx: Context) -> None:
        self.context = ctx
        self.dj = ctx.author
        self.guild_settings = await self.bot.guild_settings_service.get_safe(
            ctx.guild.id,
        )
