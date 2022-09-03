from __future__ import annotations

import discord
from discord.ext import commands


class Information(commands.Cog):
    """
    Retrieve information about various items.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if user.activity is not None:
            game = user.activity.name
        else:
            game = None
        voice_state = None if not user.voice else user.voice.channel
        embed = discord.Embed(
            timestamp=ctx.message.created_at,
            colour=self.bot.config.color,
        )
        embed_values = {
            "User ID": user.id,
            "Nick": user.nick,
            "Status": user.status,
            "On Mobile": user.is_on_mobile(),
            "In Voice": voice_state,
            "Game": game,
            "Highest Role": user.top_role.name,
            "Account Created": user.created_at.__format__("%A, %d. %B %Y @ %H:%M:%S"),
            "Join Date": user.joined_at.__format__("%A, %d. %B %Y @ %H:%M:%S"),
        }
        for n, v in embed_values.items():
            embed.add_field(name=n, value=v, inline=True)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)
        channel_count = len(
            [
                x
                for x in ctx.guild.channels
                if isinstance(x, discord.channel.TextChannel)
            ],
        )
        embed = discord.Embed(
            color=self.bot.config.color,
            timestamp=ctx.message.created_at,
        )
        embed_values = {
            "Name (ID)": (f"{ctx.guild.name} ({ctx.guild.id})", False),
            "Owner": (ctx.guild.owner, False),
            "Member Count": (ctx.guild.member_count, True),
            "Text Channels": (str(channel_count), True),
            "Region": (ctx.guild.region, True),
            "Verification Level": (str(ctx.guild.verification_level), True),
            "Highest Role": (ctx.guild.roles[-1], True),
            "Number of Roles": (str(role_count), True),
            "Number of Emotes": (str(emoji_count), True),
            "Created On": (
                ctx.guild.created_at.__format__("%A, %d. %B %Y @ %H:%M:%S"),
                True,
            ),
        }
        for n, v in embed_values.items():
            embed.add_field(name=n, value=v[0], inline=v[1])
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Information(bot))
