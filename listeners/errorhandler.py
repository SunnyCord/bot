import sys
import discord
import traceback
from discord.ext import commands
import classes.exceptions as Exceptions

class CommandErrorHandler(commands.Cog, name="Error Handler"):
    """Handles any errors that may occur."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"``{ctx.command}`` has been disabled.")

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(f"You do not have the required permission for ``{ctx.command}``.")

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send("Slow down! You are on a %.2fs cooldown." % error.retry_after)

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

        elif isinstance(error, Exceptions.OsuAPIError):
            if error.queryType == "get_user":
                return await ctx.send(f"User has not been found on {error.server.name_full} or has not played enough!")
            elif error.queryType == "get_beatmap":
                return await ctx.send(f"Beatmap was not found on {error.server.name_full}!")
            elif error.queryType == "get_recent":
                return await ctx.send(f"User has no recent plays on {error.server.name_full}!")
            elif error.queryType == "get_user_top":
                return await ctx.send(f"User has no top plays on {error.server.name_full}!")
            elif error.queryType == "get_user_scores":
                return await ctx.send(f"User has no scores on this beatmap on {error.server.name_full}!")
            else:
                return await ctx.send("Unknown API error.")

        elif isinstance(error, Exceptions.DatabaseMissingError):
            if  error.queryType == "osu":
                return await ctx.send("Please set your profile!")
            else:
                return await ctx.send("Unknown database error.")

        elif isinstance(error, Exceptions.MusicPlayerError):
            return await ctx.send(error)

        exc = f'{type(error).__name__}'
        embed = discord.Embed(title="Oh no! An error has occured", color=discord.Color.red())
        embed.add_field(name="Error:", value=f"{exc}\nIf you can, please open an issue: https://github.com/NiceAesth/Sunny/issues")
        embed.set_thumbnail(url="https://i.imgur.com/szL6ReL.png")
        await ctx.send(embed=embed)
        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
