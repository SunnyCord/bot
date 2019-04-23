import discord
from discord.ext import commands
from commons import checks
from asyncio import sleep

class Admin(commands.Cog):
    """Commands for managing Discord servers."""
    def __init__(self,bot):
        self.bot = bot

    @checks.can_kick()
    @commands.command()
    async def kick(self, ctx, user : discord.Member):
        """Kicks a user from the server."""
        if ctx.author == user:
            await ctx.send("You cannot kick yourself.")
        else:
            await user.kick()
            embed = discord.Embed(title=f'User {user.name} has been kicked.', color=0x00ff00)
            embed.add_field(name="Goodbye!", value=":boot:")
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

    @checks.can_ban()
    @commands.command()
    async def ban(self, ctx, user : discord.Member):
        """Bans a user from the server."""
        if ctx.author == user:
            await ctx.send("You cannot ban yourself.")
        else:
            await user.ban()
            embed = discord.Embed(title=f'User {user.name} has been banned.', color=0x00ff00)
            embed.add_field(name="Goodbye!", value=":hammer:")
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)

    @checks.can_mute()
    @commands.command()
    async def mute(self, ctx, user : discord.Member, time: int):
        """Prevents a user from speaking for a specified amount of time."""
        if ctx.author == user:
            await ctx.send("You cannot mute yourself.")
        else:
            rolem = discord.utils.get(ctx.message.guild.roles, name='Muted')
            if rolem is None:
                embed=discord.Embed(title="Muted role", url="http://echo-bot.wikia.com/wiki/Setting_up_the_muted_role", description="The mute command requires a role named 'Muted'.", color=0xff0000)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                embed.set_footer(text="Without this role, the command will not work.")
                await ctx.send(embed=embed)
            elif rolem not in user.roles:
                embed = discord.Embed(title=f'User {user.name} has been successfully muted for {time}s.', color=0x00ff00)
                embed.add_field(name="Shhh!", value=":zipper_mouth:")
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.send(embed=embed)
                await user.add_roles(rolem)
                await sleep(time)
                if rolem in user.roles:
                    try:
                        await user.remove_roles(rolem)
                        embed = discord.Embed(title=f'User {user.name} has been automatically unmuted.', color=0x00ff00)
                        embed.add_field(name="Welcome back!", value=":open_mouth:")
                        embed.set_thumbnail(url=user.avatar_url)
                        await ctx.send(embed=embed)
                    except Exception:
                        pass
            else:
                await ctx.send(f'User {user.mention} is already muted.')

    @checks.can_mute()
    @commands.command()
    async def unmute(self, ctx, user: discord.Member):
        """Unmutes a user."""
        rolem = discord.utils.get(ctx.message.guild.roles, name='Muted')
        if rolem in user.roles:
            embed = discord.Embed(title=f'User {user.name} has been manually unmuted.', color=0x00ff00)
            embed.add_field(name="Welcome back!", value=":open_mouth:")
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
            await user.remove_roles(rolem)

    @checks.can_managemsg()
    @commands.command()
    async def prune(self, ctx, count: int):
        """Deletes a specified amount of messages. (Max 100)"""
        if count>100:
            count = 100
        await ctx.message.channel.purge(limit=count, bulk=True)

    @checks.can_managemsg()
    @commands.command()
    async def clean(self, ctx):
        """Cleans the chat of the bot's messages."""
        def is_me(m):
            return m.author == self.bot.user
        await ctx.message.channel.purge(limit=100, check=is_me)

def setup(bot):
    bot.add_cog(Admin(bot))