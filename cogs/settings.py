import discord
from discord.ext import commands
from commons import mongoIO
from commons import checks
import config as cfg
from datetime import datetime
import time
disableKeywords = ['none','disable','off','disabled']

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

class Settings(commands.Cog):
    """Commands user for changing server-based settings."""
    def __init__(self,bot):
        self.bot = bot

    @checks.is_admin()
    @checks.is_blacklisted()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def prefix(self, ctx, prefix: str):
        """Sets the server-wide prefix."""
        if prefix.lower() in disableKeywords:
            mongoIO.setPrefix(ctx.message.guild, None)
            prefix="turned off"
        else:
            if len(prefix) > 6:
                await ctx.send("Prefix longer than 6 characters. Shortening")
                prefix = prefix[:6]
            mongoIO.setPrefix(ctx.message.guild, prefix)
        embed=discord.Embed(title="Setting updated", description=f'Server-wide prefix is now {prefix}', color=get_config().COLOR, timestamp=datetime.utcnow())
        embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url="https://i.imgur.com/ubhUTNH.gif")
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def rebuild(self, ctx, *, args = "normal"):
        """Rebuilds the database. (Owner-only)"""
        start_time = time.time()
        mongoIO.wipe()
        servers = list(self.bot.guilds)
        args = args.lower()
        for x in range(len(servers)):
            if args == "debug":
                print (f'Adding server {servers[x-1].name}')
            mongoIO.addServer(servers[x-1])
            for member in servers[x-1].members:
                if not member.bot and not mongoIO.userExists(member):
                    if args == "debug":
                        print (f'Adding member {member.name}')
                    mongoIO.addUser(member)
        await ctx.send(f'Done rebuilding. {time.time() - start_time}s')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def blacklist(self, ctx, user: discord.Member):
        """Blacklists a user from the bot. (Owner-only)"""
        if not mongoIO.userExists(user):
            mongoIO.addUser(user, True)
            await ctx.send("User blacklisted.")
        else:
            mongoIO.blacklistUser(user)
            await ctx.send("User blacklisted.")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unblacklist(self, ctx, user: discord.Member):
        """Unblacklists a user from the bot. (Owner-only)"""
        mongoIO.unblacklistUser(user)
        await ctx.send("User unblacklisted.")

    async def on_guild_join(self, guild):
        mongoIO.addServer(guild)

def setup(bot):
    bot.add_cog(Settings(bot))