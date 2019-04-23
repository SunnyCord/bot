import traceback
import sys
from discord.ext import commands
import discord

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
            return await ctx.send(f'``{ctx.command}`` has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'``{ctx.command}`` can not be used in Private Messages.')
            except:
                pass
        
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(f'You do not have the required permission for ``{ctx.command}``.')

        exc = f'{type(error).__name__}: {error}'
        embed = discord.Embed(title="Oh no! An error has occured", color=discord.Color.red())
        embed.add_field(name="Error:", value=exc)
        embed.set_thumbnail(url="https://i.imgur.com/szL6ReL.png")
        await ctx.send(embed=embed)
        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
