from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING

import aiosu
import discord
from classes import exceptions
from discord.ext import commands

if TYPE_CHECKING:
    from classes.bot import Sunny


class CommandErrorHandler(commands.Cog, name="Error Handler"):  # type: ignore
    """Handles any errors that may occur."""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

        @bot.tree.error
        async def on_app_command_error(
            interaction: discord.Interaction,
            error: Exception,
        ) -> None:
            # TODO handle slash command errors
            error = getattr(error, "original", error)
            print(error)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)
        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, discord.errors.Forbidden):
            return await ctx.send(
                f"I do not have permissions to perform ``{ctx.command}``!",
            )

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"``{ctx.command}`` has been disabled.")

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(
                f"You do not have the required permission for ``{ctx.command}``.",
            )

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(
                "Slow down! You are on a %.2fs cooldown." % error.retry_after,
            )

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

        elif isinstance(error, exceptions.OsuAPIError):
            if error.queryType == "get_user":
                return await ctx.send(
                    f"User has not been found on {error.server.name_full} or has not played enough!",
                )
            elif error.queryType == "get_beatmap":
                return await ctx.send(
                    f"Beatmap was not found on {error.server.name_full}!",
                )
            elif error.queryType == "get_recent":
                return await ctx.send(
                    f"User has no recent plays on {error.server.name_full}!",
                )
            elif error.queryType == "get_user_top":
                return await ctx.send(
                    f"User has no top plays on {error.server.name_full}!",
                )
            elif error.queryType == "get_user_scores":
                return await ctx.send(
                    f"User has no scores on this beatmap on {error.server.name_full}!",
                )
            else:
                return await ctx.send("Unknown API error.")

        elif isinstance(error, exceptions.DatabaseMissingError):
            if error.queryType == "osu":
                return await ctx.send("Please set your profile!")
            else:
                return await ctx.send("Unknown database error.")

        elif isinstance(error, exceptions.MusicPlayerError):
            return await ctx.send(error)

        exc = f"{type(error).__name__}"
        embed = discord.Embed(
            title="Oh no! An error has occured",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Error:",
            value=f"{exc}\nIf you can, please open an issue: https://github.com/NiceAesth/Sunny/issues",
        )
        embed.set_thumbnail(url="https://i.imgur.com/szL6ReL.png")
        await ctx.send(embed=embed)
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
            file=sys.stderr,
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CommandErrorHandler(bot))
