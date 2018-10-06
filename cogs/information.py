import discord
import config as cfg
from discord.ext import commands
from commons import checks

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

class Information:
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @checks.is_blacklisted()
    async def userinfo(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.message.author
        if user.activity is not None:
            game = user.activity.name
        else:
            game = None
        voice_state = None if not user.voice else user.voice.channel
        embed = discord.Embed(timestamp=ctx.message.created_at, colour=get_config().COLOR)
        embed.add_field(name='User ID', value=user.id, inline=True)
        embed.add_field(name='Nick', value=user.nick, inline=True)
        embed.add_field(name='Status', value=user.status, inline=True)
        embed.add_field(name='In Voice', value=voice_state, inline=True)
        embed.add_field(name='Game', value=game, inline=True)
        embed.add_field(name='Highest Role', value=user.top_role.name, inline=True)
        embed.add_field(name='Account Created', value=user.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), inline=True)
        embed.add_field(name='Join Date', value=user.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), inline=True)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @checks.is_blacklisted()
    async def serverinfo(self, ctx):
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)
        channel_count = len([x for x in ctx.guild.channels if type(x) == discord.channel.TextChannel])
        embed = discord.Embed(color=get_config().COLOR, timestamp=ctx.message.created_at)
        embed.add_field(name='Name (ID)', value=f"{ctx.guild.name} ({ctx.guild.id})")
        embed.add_field(name='Owner', value=ctx.guild.owner, inline=False)
        embed.add_field(name='Members', value=ctx.guild.member_count)
        embed.add_field(name='Text Channels', value=str(channel_count))
        embed.add_field(name='Region', value=ctx.guild.region)
        embed.add_field(name='Verification Level', value=str(ctx.guild.verification_level))
        embed.add_field(name='Highest role', value=ctx.guild.roles[0])
        embed.add_field(name='Number of roles', value=str(role_count))
        embed.add_field(name='Number of emotes', value=str(emoji_count))
        embed.add_field(name='Created At', value=ctx.guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)
    

def setup(bot):
    bot.add_cog(Information(bot))