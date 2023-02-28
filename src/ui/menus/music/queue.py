###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle
from discord import Interaction
from discord.ui import button
from ui.embeds.music import MusicTrackEmbed
from ui.menus.generic import BaseView

if TYPE_CHECKING:
    from typing import Any
    from pomice import Track
    from pomice import Queue
    from discord.ext.commands import Context


def _split_queue_to_pages(
    ctx: Context,
    queue: list[Track],
    title: str,
) -> list[MusicTrackEmbed]:
    embeds: list[MusicTrackEmbed] = [
        MusicTrackEmbed(ctx, track, title) for track in queue
    ]

    return embeds


class MusicQueueView(BaseView):
    def __init__(
        self,
        ctx: Context,
        queue: Queue,
        results: list[Track] | None = None,
        title: str = "Queued up",
        *args: Any,
        **kwargs: Any,
    ):
        self.ctx = ctx
        self.message = ctx.message
        self.bot = ctx.bot
        self.author = ctx.author
        self.queue = queue

        super().__init__(*args, **kwargs)

        if results:
            display_tracks = results
            self.remove_item(self.stop_button)
        else:
            display_tracks = queue.get_queue()
            self.remove_item(self.play_button)
        self._redo_rows()

        self._embeds = _split_queue_to_pages(self.ctx, display_tracks, title)
        self._current = 0

        for i, embed in enumerate(self._embeds):
            footer = embed.footer.text
            embed.set_footer(text=f"Track {i+1}/{self._len} | {footer}")

        if self._len <= 1:
            self._stop()
        else:
            self._check_buttons()

    @property
    def initial(self) -> MusicTrackEmbed:
        return self._embeds[0]

    @property
    def _len(self) -> int:
        return len(self._embeds)

    def _redo_rows(self) -> None:
        self.remove_item(self.last_embed_button)
        self.last_embed_button.row = 0
        self.add_item(self.last_embed_button)

    def _get_embed(self) -> MusicTrackEmbed:
        return self._embeds[self._current]

    def _check_buttons(self) -> None:
        if self._current == 0:
            self.first_embed_button.disabled = True
        else:
            self.first_embed_button.disabled = False
        if self._current == self._len - 1:
            self.last_embed_button.disabled = True
        else:
            self.last_embed_button.disabled = False

    def _previous_embed(self) -> None:
        self._current = (self._current - 1) % self._len
        self._check_buttons()

    def _next_embed(self) -> None:
        self._current = (self._current + 1) % self._len
        self._check_buttons()

    def _stop(self) -> None:
        self.clear_items()
        self.stop()

    @button(emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}", row=0)
    async def first_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._current = 0
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="\N{LEFTWARDS BLACK ARROW}")
    async def previous_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._previous_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="\N{BLACK SQUARE FOR STOP}")
    async def stop_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._stop()
        await interaction.response.edit_message(view=self)

    @button(emoji="\N{WHITE HEAVY CHECK MARK}", style=ButtonStyle.green)
    async def play_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        current_embed = self._get_embed()
        track = current_embed.track
        self.queue.put(track)
        await interaction.response.send_message(
            # check if has author track.title otherwise
            f"Added track {current_embed.title_str} to queue.",
            ephemeral=True,
        )

    @button(emoji="\N{BLACK RIGHTWARDS ARROW}")
    async def next_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._next_embed()
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
    async def last_embed_button(
        self,
        interaction: Interaction,
        button: button.Button,
    ) -> None:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You are not the author of this message.",
                ephemeral=True,
            )
            return
        self._current = self._len - 1
        embed = self._get_embed()
        await embed.prepare()
        await interaction.response.edit_message(embed=embed, view=self)
