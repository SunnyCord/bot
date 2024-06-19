###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import asyncio
from abc import ABC
from abc import abstractmethod
from io import BytesIO
from typing import TYPE_CHECKING

import discord
from discord import File

from common import humanizer

if TYPE_CHECKING:
    from typing import Any

    from aiosu.models import Beatmapset
    from aiosu.models import Gamemode
    from discord import Interaction


class OsudleSkipButton(discord.ui.Button["BaseOsudleGame"]):
    def __init__(self, game: BaseOsudleGame) -> None:
        super().__init__(style=discord.ButtonStyle.danger, label="Skip")
        self.game = game

    async def callback(self, _: discord.Interaction):
        self.game.skip()


class BaseOsudleGame(ABC):
    __slots__ = (
        "interaction",
        "running",
        "stop_event",
        "mode",
        "current_task",
        "current_beatmapset",
        "timeout",
        "scores",
        "current_view",
        "latest_beatmap_message",
    )

    def __init__(self) -> None:
        self.interaction = None
        self.running = False
        self.stop_event = asyncio.Event()
        self.mode = None
        self.current_task = None
        self.current_beatmapset = None
        self.timeout = 60
        self.scores = {}
        self.current_view = None
        self.latest_beatmap_message = None

    def get_formatted_scoreboard(self) -> str:
        if not self.scores:
            return "\nNobody got any points. :("

        return "\n".join(
            f"### {i + 1}. <@{user}> - {score} guesses"
            for i, (user, score) in enumerate(
                sorted(self.scores.items(), key=lambda x: x[1], reverse=True)[:3],
            )
        )

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
            return await self.interaction.followup.send(*args, **kwargs)
        try:
            return await self.interaction.response.send_message(*args, **kwargs)
        except discord.HTTPException:
            return await self.interaction.followup.send(*args, **kwargs)

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

        self.scores[message.author.id] = self.scores.get(message.author.id, 0) + 1
        await message.reply(
            f"Correct! {message.author.mention} guessed **{beatmapset.title}** by **{beatmapset.artist}**.",
        )

    async def edit_latest_message(self, *args, **kwargs) -> None:
        if self.latest_beatmap_message:
            return await self.latest_beatmap_message.edit(*args, **kwargs)
        await self.interaction.edit_original_response(*args, **kwargs)

    async def remove_view(self) -> None:
        if not self.current_view:
            return

        self.current_view.stop()
        self.current_view = None
        await self.edit_latest_message(view=None)

    async def do_next(self) -> None:
        if self.current_task:
            raise RuntimeError("Task already running.")

        await self.remove_view()

        beatmapset = await self.get_beatmapset()
        await self.send_message(beatmapset)

        try:
            self.current_task = asyncio.create_task(
                self.wait_for_guess(beatmapset),
            )
            await self.current_task
            self.current_task = None
        except asyncio.CancelledError:
            await self.send_response(
                f"**{beatmapset.title}** by **{beatmapset.artist}** was the correct answer.",
            )
        except asyncio.TimeoutError:
            await self.send_response(
                f"Nobody guessed the song. The correct answer was **{beatmapset.title}** by **{beatmapset.artist}**.",
            )
            await self.stop_game()
            raise

    def skip(self) -> None:
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None

    async def start_game(self, interaction: Interaction, mode: Gamemode) -> None:
        self.running = True
        self.stop_event.clear()
        self.interaction = interaction
        self.mode = mode

        while not self.stop_event.is_set():
            await self.do_next()

        await self.stop_game()

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

        await self.remove_view()

        if not self.running or self.stop_event.is_set():
            return

        self.stop_event.set()
        self.running = False

        await self.send_response(
            f"Game has stopped.\nFinal scoreboard:\n{self.get_formatted_scoreboard()}",
        )

    async def send_message(self, beatmapset: Beatmapset) -> None:
        content = await self.get_message_content(beatmapset)
        self.current_view = discord.ui.View()
        self.current_view.add_item(OsudleSkipButton(self))
        self.latest_beatmap_message = await self.send_response(
            **content,
            view=self.current_view,
        )

    @abstractmethod
    async def get_message_content(self, beatmapset: Beatmapset) -> dict[str, Any]: ...


class OsudleSongGame(BaseOsudleGame):
    """osu! Song Preview Game"""

    async def get_message_content(self, beatmapset: Beatmapset) -> dict[str, Any]:
        async with self.interaction.client.aiohttp_session.get(
            f"https:{beatmapset.preview_url}",
        ) as resp:
            if resp.status != 200:
                await self.send_response("Failed to fetch the audio file.")
                await self.stop_game()
                return
            file_bytes = BytesIO(await resp.read())
            audio_file = File(file_bytes, filename="Preview.mp3")
            return {
                "file": audio_file,
            }


class OsudleBackgroundGame(BaseOsudleGame):
    """osu! Background Game"""

    async def get_message_content(self, beatmapset: Beatmapset) -> dict[str, Any]:
        cover_url = beatmapset.covers.cover_2_x.replace(r"https:\/\/", "https://")
        async with self.interaction.client.aiohttp_session.get(cover_url) as resp:
            if resp.status != 200:
                await self.send_response("Failed to fetch the background image.")
                await self.stop_game()
                return
            file_bytes = BytesIO(await resp.read())
            image_file = File(file_bytes, filename="Background.jpg")
            return {
                "file": image_file,
            }
