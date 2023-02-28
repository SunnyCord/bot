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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.loop_mode: pomice.LoopMode = kwargs.pop("loop_mode", pomice.LoopMode.QUEUE)
        super().__init__(*args, **kwargs)

        self.queue: pomice.Queue = pomice.Queue()
        self.controller: Message | None = None
        self.context: Context | None = None
        self.guild_settings: GuildSettings | None = None
        self.dj: Member | None = None

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()

    def set_loop_mode(self, loop_mode: pomice.LoopMode) -> None:
        self.loop_mode = loop_mode
        self.queue.set_loop_mode(loop_mode)

    def disable_loop(self) -> None:
        if self.queue.is_looping:
            self.queue.disable_loop()
            return

    async def do_next(self) -> None:
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        if self.controller:
            with suppress(HTTPException):
                await self.controller.delete()

        try:
            track: pomice.Track = self.queue.get()
        except pomice.QueueEmpty:
            if self.guild_settings.voice_auto_disconnect:
                await self.teardown()
            return

        await self.play(track)

        self.controller = await self.context.send(
            embed=MusicTrackEmbed(self.context, track),
        )

    async def teardown(self) -> None:
        with suppress((HTTPException), (KeyError)):
            await self.destroy()
            if self.controller:
                await self.controller.delete()

    async def set_context(self, ctx: Context) -> None:
        self.context = ctx
        self.dj = ctx.author
        self.guild_settings = await self.bot.guild_settings_service.get_safe(
            ctx.guild.id,
        )
