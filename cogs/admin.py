from __future__ import annotations

import datetime

import discord
from discord.ext import commands
from pytimeparse.timeparse import timeparse

from commons import checks


class Admin(commands.Cog):
    """
    Commands for managing Discord servers.
    """

    def __init__(self, bot):
        self.bot = bot

    @checks.can_kick()
    @commands.command()
    async def kick(self, ctx, user: discord.Member):
        """Kicks a user from the server."""
        if ctx.author == user:
            return await ctx.send("You cannot kick yourself.")
        await user.kick()
        embed = discord.Embed(
            title=f"User {user.name} has been kicked.",
            color=0x00FF00,
        )
        embed.add_field(name="Goodbye!", value=":boot:")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @checks.can_ban()
    @commands.command()
    async def ban(self, ctx, user: discord.Member):
        """Bans a user from the server."""
        if ctx.author == user:
            return await ctx.send("You cannot ban yourself.")
        await user.ban()
        embed = discord.Embed(
            title=f"User {user.name} has been banned.",
            color=0x00FF00,
        )
        embed.add_field(name="Goodbye!", value=":hammer:")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @checks.can_mute()
    @commands.command()
    async def mute(self, ctx, user: discord.Member, time: str):
        """Prevents a user from speaking for a specified amount of time."""
        if ctx.author == user:
            return await ctx.send("You cannot mute yourself.")
        if (rolem := discord.utils.get(ctx.guild.roles, name="Muted")) is None:
            return ctx.send("You have not set up the 'Muted' role!")
        if rolem in user.roles:
            return await ctx.send(f"User {user.mention} is already muted.")
        await user.add_roles(rolem)
        if time.isnumeric():
            time += "s"
        duration = datetime.timedelta(seconds=timeparse(time))
        ends = datetime.datetime.utcnow() + duration
        await self.bot.mongoIO.muteUser(user, ctx.guild, ends)
        embed = discord.Embed(
            title=f"User {user.name} has been successfully muted for {duration}",
            color=0x00FF00,
        )
        embed.add_field(name="Shhh!", value=":zipper_mouth:")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @checks.can_mute()
    @commands.command()
    async def unmute(self, ctx, user: discord.Member):
        """Unmutes a user."""
        rolem = discord.utils.get(ctx.guild.roles, name="Muted")
        if rolem not in user.roles:
            return await ctx.send("User is not muted.")
        embed = discord.Embed(
            title=f"User {user.name} has been unmuted.",
            color=0x00FF00,
        )
        embed.add_field(name="Welcome back!", value=":open_mouth:")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)
        await user.remove_roles(rolem)
        await self.bot.mongoIO.unmuteUser(user, ctx.guild)

    @checks.can_managemsg()
    @commands.command()
    async def prune(self, ctx, count: int):
        """Deletes a specified amount of messages. (Max 100)"""
        count = max(1, min(count, 100))
        await ctx.message.channel.purge(limit=count, bulk=True)

    @checks.can_managemsg()
    @commands.command()
    async def clean(self, ctx):
        """Cleans the chat of the bot's messages."""

        def is_me(m):
            return m.author == self.bot.user

        await ctx.message.channel.purge(limit=100, check=is_me)


async def setup(bot):
    await bot.add_cog(Admin(bot))
