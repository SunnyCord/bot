###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import asyncio
from abc import ABC
from abc import abstractmethod
from io import BytesIO
from typing import TYPE_CHECKING

from common import humanizer
from discord import File

if TYPE_CHECKING:
    from aiosu.models import Beatmapset
    from aiosu.models import Gamemode
    from discord import Interaction


class BaseOsudleGame(ABC):
    __slots__ = (
        "interaction",
        "running",
        "stop_event",
        "mode",
        "current_task",
        "current_beatmapset",
        "timeout",
    )

    def __init__(self) -> None:
        self.interaction = None
        self.running = False
        self.stop_event = asyncio.Event()
        self.mode = None
        self.current_task = None
        self.current_beatmapset = None
        self.timeout = 60

    def check_guess(self, message: str) -> bool:
        return (
            message.channel is self.interaction.channel
            and not message.author.bot
            and humanizer.song_title_match(
                message.content,
                self.current_beatmapset.title,
            )
        )

    async def send_response(self, *args, **kwargs) -> None:
        if self.interaction.response.is_done():
            await self.interaction.followup.send(*args, **kwargs)
            return
        await self.interaction.response.send_message(*args, **kwargs)

    async def get_beatmapset(self) -> Beatmapset:
        self.current_beatmapset = (
            await self.interaction.client.beatmapset_service.get_random(self.mode)
        )
        return self.current_beatmapset

    async def wait_for_guess(self, beatmapset: Beatmapset) -> None:
        message = await self.interaction.client.wait_for(
            "message",
            check=self.check_guess,
            timeout=self.timeout,
        )

        await message.reply(
            f"Correct! {message.author.mention} guessed **{beatmapset.title}** by **{beatmapset.artist}**.",
        )

    async def do_next(self) -> None:
        while not self.stop_event.is_set():
            if self.current_task:
                await self.send_response(
                    f"**{self.current_beatmapset.title}** by **{self.current_beatmapset.artist}** was the correct answer.",
                )
                self.current_task.cancel()
                try:
                    await self.current_task
                except asyncio.CancelledError:
                    pass
                self.current_task = None

            beatmapset = await self.get_beatmapset()
            await self.send_message(beatmapset)

            try:
                self.current_task = asyncio.create_task(self.wait_for_guess(beatmapset))
                await self.current_task
                self.current_task = None
            except asyncio.TimeoutError:
                await self.send_response(
                    f"**{beatmapset.title}** by **{beatmapset.artist}** was the correct answer.",
                )
                await self.stop_game()
                raise

    async def start_game(self, interaction: Interaction, mode: Gamemode) -> None:
        self.running = True
        self.stop_event.clear()
        self.interaction = interaction
        self.mode = mode

        while not self.stop_event.is_set():
            if self.stop_event.is_set():
                break

            await self.do_next()

        self.running = False

    async def stop_game(self) -> None:
        if self.current_task:
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                pass
            self.current_task = None

        self.stop_event.set()
        await self.send_response("Game stopped.")

    @abstractmethod
    async def send_message(self, beatmapset: Beatmapset) -> None:
        ...


class OsudleSongGame(BaseOsudleGame):
    """osu! Song Preview Game"""

    async def send_message(self, beatmapset: Beatmapset) -> None:
        async with self.interaction.client.aiohttp_session.get(
            f"https:{beatmapset.preview_url}",
        ) as resp:
            if resp.status != 200:
                await self.send_response("Failed to fetch the audio file.")
                await self.stop_game()
                return
            file_bytes = BytesIO(await resp.read())
            audio_file = File(file_bytes, filename="Preview.mp3")
            await self.send_response(file=audio_file)


class OsudleBackgroundGame(BaseOsudleGame):
    """osu! Background Game"""

    async def send_message(self, beatmapset: Beatmapset) -> None:
        cover_url = beatmapset.covers.cover_2_x.replace(r"https:\/\/", "https://")
        async with self.interaction.client.aiohttp_session.get(cover_url) as resp:
            if resp.status != 200:
                await self.send_response("Failed to fetch the background image.")
                await self.stop_game()
                return
            file_bytes = BytesIO(await resp.read())
            image_file = File(file_bytes, filename="Background.jpg")
            await self.send_response(file=image_file)
