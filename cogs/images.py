import discord
from discord.ext import commands
import aiohttp
from commons import checks

class Image(commands.Cog):
    """Various image-related commands."""
    def __init__(self,bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def cat(self, ctx):
        """Sends a cute cat picture."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://aws.random.cat//meow') as r:
                res = await r.json()
                await ctx.send(res['file'])

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def dog(self, ctx):
        """Who doesn't love a good dog pic?"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://dog.ceo/api/breeds/image/random') as r:
                res = await r.json()
                await ctx.send(res['message'])      

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def avatar(self, ctx, user : discord.Member = None):
        """Gets a user's avatar. Returns invoker's avatar if no user is specified."""
        if user is None:
            await ctx.send(ctx.message.author.avatar_url)
        else:
            await ctx.send(user.avatar_url)

def setup(bot):
    bot.add_cog(Image(bot))