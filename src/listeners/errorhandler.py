###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import aiosu
import discord
from classes import exceptions
from classes.cog import MetadataCog
from common.logging import logger
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from classes.bot import Sunny
    from typing import Callable


class CommandErrorHandler(MetadataCog, name="Error Handler", hidden=True):
    """Handles any errors that may occur."""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

        @bot.tree.error
        async def on_app_command_error(
            interaction: discord.Interaction,
            error: Exception,
        ) -> None:
            await self.error_handler(
                interaction.response.send_message,
                interaction.command,
                error,
                True,
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await self.error_handler(ctx.send, ctx.command, error)

    async def error_handler(
        self,
        send_message: Callable,
        command: commands.Command,
        error: Exception,
        is_slash: bool = False,
    ) -> None:
        if hasattr(command, "on_error") and not is_slash:
            return

        while hasattr(error, "original"):
            error = error.original

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.BotMissingPermissions):
            return await send_message(
                f"I am missing the following permissions: ``{', '.join(error.missing_permissions)}`` for ``{command}``.",
            )

        elif isinstance(error, commands.MissingPermissions):
            return await send_message(
                f"You are missing the following permissions: ``{', '.join(error.missing_permissions)}`` for ``{command}``.",
            )

        elif isinstance(error, discord.errors.Forbidden):
            return await send_message(
                f"I do not have permissions to perform ``{command}``!",
            )

        elif isinstance(error, commands.DisabledCommand):
            return await send_message(f"``{command}`` has been disabled.")

        elif isinstance(error, commands.CommandOnCooldown):
            return await send_message(
                "Slow down! You are on a %.2fs cooldown." % error.retry_after,
            )

        elif isinstance(error, commands.RangeError):
            return await send_message(
                f"Value must be between **{error.minimum}** and **{error.maximum}**.",
            )

        elif isinstance(error, aiosu.exceptions.APIException):
            logger.exception(
                f"An osu! API error has occured in command {command}: ",
                exc_info=error,
            )
            return await send_message("An osu! API error has occured.")

        elif isinstance(error, aiosu.exceptions.InvalidClientRequestedError):
            return await send_message(
                "Please set your profile! Use the ``osuset`` command.",
            )

        elif isinstance(error, exceptions.MusicPlayerError):
            return await send_message(error)

        exc = f"{type(error).__name__}"
        embed = discord.Embed(
            title="Oh no! An unexpected error has occured",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Error:",
            value=f"{exc}\nIf you can, please open an issue: https://github.com/SunnyCord/bot/issues",
        )
        # TODO: Error ID, so we can track errors and remove traceback from embed
        embed.set_thumbnail(url="https://i.imgur.com/szL6ReL.png")
        await send_message(embed=embed)

        logger.exception(
            f"Ignoring exception in command {command}: ",
            exc_info=error,
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CommandErrorHandler(bot))
