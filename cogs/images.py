import discord
from discord.ext import commands
import aiohttp

class Image(commands.Cog):
    """Various image-related commands."""
    def __init__(self,bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def cat(self, ctx):
        """Sends a random cat image and fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/cat') as r:
                res = await r.json()
                imgUrl = res['link']
            async with cs.get('https://some-random-api.ml/facts/cat') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐈', description=f"**Cat Fact:**\n{fact}", color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def dog(self, ctx):
        """Sends a random dog image and fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/dog') as r:
                res = await r.json()
                imgUrl = res['link']
            async with cs.get('https://some-random-api.ml/facts/dog') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐕', description=f"**Dog Fact:**\n{fact}", color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def fox(self, ctx):
        """Sends a random fox image and fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/fox') as r:
                res = await r.json()
                imgUrl = res['link']
            async with cs.get('https://some-random-api.ml/facts/fox') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🦊', description=f"**Fox Fact:**\n{fact}", color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def bird(self, ctx):
        """Sends a random bird image and fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/birb') as r:
                res = await r.json()
                imgUrl = res['link']
            async with cs.get('https://some-random-api.ml/facts/bird') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐦', description=f"**Bird Fact:**\n{fact}", color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def duck(self, ctx):
        """Sends a random duck image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/v2/random') as r:
                res = await r.json()
                imgUrl = res['url']
        embed = discord.Embed(title='🦆', color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def panda(self, ctx):
        """Sends a random panda image and fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/panda') as r:
                res = await r.json()
                imgUrl = res['link']
            async with cs.get('https://some-random-api.ml/facts/panda') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐼', description=f"**Panda Fact:**\n{fact}", color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def koala(self, ctx):
        """Sends a random koala image and fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/koala') as r:
                res = await r.json()
                imgUrl = res['link']
            async with cs.get('https://some-random-api.ml/facts/koala') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐨', description=f"**Koala Fact:**\n{fact}", color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def wink(self, ctx):
        """😉"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/animu/wink') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title=f'{ctx.message.author.name} winks 😉', color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def pat(self, ctx, user: discord.Member = None):
        """Pat someone (or yourself)."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/animu/pat') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title=f'{ctx.message.author.name} pats {f"themselves. 😔" if user is None else f"{user.name} <:angery:545969728527663114>"}', color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """Hug someone (or yourself)."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/animu/hug') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title=f'{ctx.message.author.name} hugs {f"themselves. 😔" if user is None else f"{user.name} <:angery:545969728527663114>"}', color=self.bot.config.color).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def avatar(self, ctx, user : discord.Member = None):
        """Gets a user's avatar. Returns invoker's avatar if no user is specified."""
        embed = discord.Embed(title=f"{ctx.message.author.name if user is None else user.name}'s avatar.", color=self.bot.config.color).set_image(url=ctx.message.author.avatar_url if user is None else user.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Image(bot))
