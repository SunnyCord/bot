###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from contextlib import suppress
from random import choice
from random import randint
from typing import TYPE_CHECKING

import discord
from classes.cog import MetadataCog
from discord import app_commands
from discord.ext import commands
from ui.embeds.fun import PollEmbed

if TYPE_CHECKING:
    from classes.bot import Sunny

EIGHT_BALL_RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]


class Fun(MetadataCog):
    """
    Miscellaneous commands.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="poll", description="Creates a reaction poll")
    @app_commands.describe(text="Text for the poll")
    async def poll_command(self, ctx: commands.Context, *, text: str) -> None:
        with suppress(discord.HTTPException):
            await ctx.message.delete()

        embed = PollEmbed(ctx, text)

        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await message.add_reaction("🤷")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(name="ping", description="Pings the bot")
    async def ping_command(self, ctx: commands.Context) -> None:
        await ctx.send(
            f"🏓 Pong!: {self.bot.latency*1000:.2f}ms",
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(name="roll", description="Roll a random number")
    @app_commands.describe(maximum="Maximum number to roll")
    async def roll_command(
        self,
        ctx: commands.Context,
        maximum: commands.Range[int, 2, 100] = 100,
    ) -> None:
        await ctx.send(f"🎲 Rolled: **{randint(1, maximum)}**")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(name="flip", description="Flip a coin")
    async def flip_command(self, ctx: commands.Context) -> None:
        await ctx.send(f"🪙 Flipped: **{'Heads' if randint(0, 1) else 'Tails'}**")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball")
    @app_commands.describe(question="Question to ask")
    async def eightball_command(self, ctx: commands.Context, *, question: str) -> None:
        await ctx.send(f"🎱 Answer: **{choice(EIGHT_BALL_RESPONSES)}**")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(name="duel", description="Duel another user")
    @app_commands.describe(user="User to duel")
    async def duel_command(self, ctx: commands.Context, user: discord.User) -> None:
        if user == ctx.author:
            await ctx.send("You can't duel yourself!")
            return

        if user.bot:
            await ctx.send("You can't duel a bot!")
            return

        await ctx.send(
            f"{ctx.author.mention} and {user.mention} dueled for **{randint(2, 120)}** hours! It was a long battle, but {choice([ctx.author.mention, user.mention])} came out victorious!",
            silent=True,
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(
        name="love",
        description="Calculate the love between two users",
    )
    @app_commands.describe(user="User to calculate love with")
    async def love_command(self, ctx: commands.Context, user: discord.User) -> None:
        if user == ctx.author:
            await ctx.send("You can't love yourself!")
            return

        if user.bot:
            await ctx.send("You can't love a bot!")
            return

        love_percentage = (ctx.author.id + user.id) % 100

        await ctx.send(
            f"{ctx.author.mention} and {user.mention} love each other **{love_percentage}%**!",
            silent=True,
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Fun(bot))
