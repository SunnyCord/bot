###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import aiordr
import aiosu
import discord
import pomice
import sentry_sdk
from classes import exceptions
from classes.cog import MetadataCog
from common.logging import logger
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
        if not isinstance(error, commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)
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
            await send_message(
                f"I am missing the following permissions: ``{', '.join(error.missing_permissions)}`` for ``{command}``.",
            )
            return

        elif isinstance(error, commands.MissingPermissions):
            await send_message(
                f"You are missing the following permissions: ``{', '.join(error.missing_permissions)}`` for ``{command}``.",
            )
            return

        elif isinstance(error, discord.errors.Forbidden):
            await send_message(
                f"I do not have permissions to perform ``{command}``!",
            )
            return

        elif isinstance(error, commands.NotOwner):
            await send_message("You are not the owner of this bot.")
            return

        elif isinstance(error, commands.DisabledCommand):
            await send_message(f"``{command}`` has been disabled.")
            return

        elif isinstance(error, commands.CommandOnCooldown):
            await send_message(
                f"Slow down! You are on a {error.retry_after:.2f}s cooldown.",
            )
            return

        elif isinstance(error, commands.RangeError):
            await send_message(
                f"Value must be between **{error.minimum}** and **{error.maximum}**.",
            )
            return

        elif isinstance(error, commands.UserInputError):
            await send_message(
                f"Invalid input for ``{command}``. Please check your input and try again.",
            )

        elif isinstance(error, aiosu.exceptions.APIException):
            await send_message("The requested data was not found on osu!")
            return

        elif isinstance(error, aiordr.exceptions.APIException):
            await send_message(f"That didn't work. {error.message}")
            return

        elif isinstance(error, aiosu.exceptions.InvalidClientRequestedError):
            await send_message(
                "Please set your profile! Use the ``osuset`` command.",
            )
            return

        elif isinstance(error, exceptions.MusicPlayerError):
            await send_message(error, delete_after=10)
            return

        elif isinstance(error, pomice.exceptions.NoNodesAvailable):
            await send_message("No music nodes are available. Try again later!")
            return

        sentry_id = sentry_sdk.capture_exception(error)

        embed = discord.Embed(
            title="Oh no! An unexpected error has occured",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Error:",
            value=f"```ID: {sentry_id}```\nProvide this ID if you need help. You may also join the [support server]({self.bot.config.support_invite}).",
        )
        embed.set_thumbnail(url="https://i.imgur.com/szL6ReL.png")
        await send_message(embed=embed)

        logger.exception(
            f"Ignoring exception in command {command}: ",
            exc_info=error,
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CommandErrorHandler(bot))
