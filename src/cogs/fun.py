from __future__ import annotations

import random
import time

import discord
from discord.ext import commands


def random_line(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)


class Fun(commands.Cog):
    """
    Miscellaneous commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def poll(self, ctx, *, args):
        """Creates a poll. Takes the polltext as an argument."""
        try:
            await ctx.message.delete()
        except:
            pass
        embed = discord.Embed(
            title="Poll:",
            description=args,
            color=self.bot.config.color,
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=random_line("commons/pollimages"))
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await message.add_reaction("🤷")

    @commands.command()
    async def ping(self, ctx):
        """Ping command."""
        t1 = time.perf_counter()
        await ctx.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send(f"🏓 Pong!: {round((t2-t1)*1000)}ms")


async def setup(bot):
    await bot.add_cog(Fun(bot))
