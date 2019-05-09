import discord
from discord.ext import commands
import random, time
import config as cfg

def random_line(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

class Fun(commands.Cog):
    """Miscellaneous commands."""
    def __init__(self,bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def poll(self, ctx, *, args):
        """Creates a poll. Takes the polltext as an argument."""
        await ctx.message.delete()
        embed=discord.Embed(title="Poll:", description=args, color=get_config().COLOR)
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url=random_line('pollimages'))
        message = await ctx.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        await message.add_reaction('🤷')

    @commands.command()
    async def ping(self,ctx):
        """Ping command."""
        t1 = time.perf_counter()
        await ctx.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send(f"🏓 Pong!: {round((t2-t1)*1000)}ms")

def setup(bot):
    bot.add_cog(Fun(bot))