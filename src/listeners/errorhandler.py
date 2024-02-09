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
from common.premium import PremiumMissing
from common.premium import SupportServerMissing
from discord.ext import commands


if TYPE_CHECKING:
    from classes.bot import Sunny
    from collections.abc import Callable


def create_sentry_scope_ctx(ctx: commands.Context) -> sentry_sdk.Scope:
    if hasattr(ctx, "transaction"):
        ctx.transaction.set_status("internal_error")

    scope = sentry_sdk.Scope()
    scope.set_user(
        {
            "id": ctx.author.id,
            "username": ctx.author.name,
        },
    )
    if ctx.command is not None:
        scope.set_tag("command", ctx.command.qualified_name)
    scope.set_tag("guild", ctx.guild.id)
    scope.set_tag("channel", ctx.channel.id)
    return scope


def create_sentry_scope_interaction(
    interaction: discord.Interaction,
) -> sentry_sdk.Scope:
    scope = sentry_sdk.Scope()
    scope.set_user(
        {
            "id": interaction.user.id,
            "username": interaction.user.name,
        },
    )
    if interaction.command is not None:
        scope.set_tag("command", interaction.command.qualified_name)
    scope.set_tag("guild", interaction.guild.id)
    scope.set_tag("channel", interaction.channel.id)
    return scope


def reply_interaction(interaction: discord.Interaction):
    async def send_message(*args, **kwargs):
        if not interaction.response.is_done():
            await interaction.response.send_message(*args, **kwargs)
        else:
            await interaction.followup.send(*args, **kwargs)

    return send_message


class CommandErrorHandler(MetadataCog, name="Error Handler", hidden=True):
    """Handles any errors that may occur."""

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.bot.tree.error(self.on_app_command_error)

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
    ) -> None:
        scope = create_sentry_scope_interaction(interaction)
        await self.error_handler(
            send_message=reply_interaction(interaction),
            command=interaction.command,
            error=error,
            scope=scope,
            is_slash=True,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            if ctx.command is not None:
                ctx.command.reset_cooldown(ctx)

        scope = create_sentry_scope_ctx(ctx)
        await self.error_handler(
            send_message=ctx.send,
            command=ctx.command,
            error=error,
            scope=scope,
            is_slash=False,
        )

        if hasattr(ctx, "transaction"):
            ctx.transaction.finish()

    async def error_handler(
        self,
        send_message: Callable,
        command: commands.Command,
        error: Exception,
        scope: sentry_sdk.Scope,
        is_slash: bool,
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
                delete_after=10,
            )
            return

        elif isinstance(error, commands.MissingPermissions):
            await send_message(
                f"You are missing the following permissions: ``{', '.join(error.missing_permissions)}`` for ``{command}``.",
                delete_after=10,
            )
            return

        elif isinstance(error, discord.errors.Forbidden):
            await send_message(
                f"I do not have permissions to perform ``{command}``!",
                delete_after=10,
            )
            return

        elif isinstance(error, commands.NotOwner):
            await send_message("You are not the owner of this bot.", delete_after=5)
            return

        elif isinstance(error, commands.DisabledCommand):
            await send_message(f"``{command}`` has been disabled.", delete_after=5)
            return

        elif isinstance(error, commands.CommandOnCooldown):
            await send_message(
                f"Slow down! You are on a {error.retry_after:.2f}s cooldown.",
                delete_after=max(error.retry_after, 1),
            )
            return

        elif isinstance(error, commands.RangeError):
            await send_message(
                f"Value must be between **{error.minimum}** and **{error.maximum}**.",
                delete_after=10,
            )
            return

        elif isinstance(error, commands.UserInputError):
            await send_message(
                f"Invalid input for ``{command}``. Please check your input and try again.",
                delete_after=10,
            )
            return

        elif isinstance(error, (SupportServerMissing, PremiumMissing)):
            await send_message(
                error,
                delete_after=30,
            )
            return

        elif isinstance(error, aiosu.exceptions.APIException):
            await send_message(
                "The requested data was not found on osu!",
                delete_after=10,
            )
            return

        elif isinstance(error, aiordr.exceptions.APIException):
            await send_message(f"That didn't work. {error.message}", delete_after=10)
            return

        elif isinstance(error, aiosu.exceptions.InvalidClientRequestedError):
            cmd_list = await self.bot.tree.fetch_commands()
            osuset_command = next(
                (c for c in cmd_list if c.name == "osuset"),
            )
            await send_message(
                f"Please set your profile! Use the {osuset_command.mention} command.",
                delete_after=20,
            )
            return

        elif isinstance(error, aiosu.exceptions.RefreshTokenExpiredError):
            cmd_list = await self.bot.tree.fetch_commands()
            osuset_command = next(
                (c for c in cmd_list if c.name == "osuset"),
            )
            await send_message(
                f"Your osu! session has expired! Use the {osuset_command.mention} command to refresh it.",
                delete_after=20,
            )
            return

        elif isinstance(error, exceptions.MusicPlayerError):
            await send_message(error, delete_after=10)
            return

        elif isinstance(error, pomice.TrackLoadError):
            await send_message(f"Failed to load this track!", delete_after=10)
            return

        sentry_id = sentry_sdk.capture_exception(
            error=error,
            scope=scope,
        )

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
