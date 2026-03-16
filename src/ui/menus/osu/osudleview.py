###
# Copyright (c) 2024 NiceAesth. All rights reserved.
###

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from classes.osudle import BaseOsudleGame


class OsudleGuessView(discord.ui.View):
    def __init__(self, game: object) -> None:
        super().__init__(timeout=game.interaction_timeout)
        self.game: BaseOsudleGame = game

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.danger)
    async def skip_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await self.game.skip(interaction)


class OsudleContinueView(discord.ui.View):
    def __init__(self, game) -> None:
        super().__init__(timeout=game.interaction_timeout)
        self.game = game

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.defer()
        self.game.last_interaction_time = time.monotonic()
        self.game.interaction = interaction
        self.stop()
