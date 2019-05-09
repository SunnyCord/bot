import discord
import config as cfg
from discord.ext import commands
import aiohttp

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

class Image(commands.Cog):
    """Various image-related commands."""
    def __init__(self,bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['kitty'])
    async def cat(self, ctx):
        """Sends a cute cat picture."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://aws.random.cat//meow') as r:
                res = await r.json()
                imgUrl = res['file']
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/facts/cat') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐈 Kitty!', description=f"**Cat Fact:**\n{fact}", color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['woof'])
    async def dog(self, ctx):
        """Who doesn't love a good dog pic?"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/dog') as r:
                res = await r.json()
                imgUrl = res['link']
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/facts/dog') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐕 Doggo!', description=f"**Dog Fact:**\n{fact}", color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['floof'])
    async def fox(self, ctx):
        """So fluffy!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/fox') as r:
                res = await r.json()
                imgUrl = res['link']
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/facts/fox') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🦊 Pure floof!', description=f"**Fox Fact:**\n{fact}", color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['pika'])
    async def pikachu(self, ctx):
        """Not the best pokemon, but one of the cutest."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/pikachuimg') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title='Pika!', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['birb'])
    async def bird(self, ctx):
        """A birb is sure to cheer you right up!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/birb') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title='🐦 Birb!', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['quack', 'duk'])
    async def duck(self, ctx):
        """Ducks are underrated."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/v2/random') as r:
                res = await r.json()
                imgUrl = res['url']
        embed = discord.Embed(title='🦆 Quack!', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def panda(self, ctx):
        """Pandas are illegally cute."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/panda') as r:
                res = await r.json()
                imgUrl = res['link']
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/facts/panda') as r:
                res = await r.json()
                fact = res['fact']
        embed = discord.Embed(title='🐼 Panda!', description=f"**Panda Fact:**\n{fact}", color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def koala(self, ctx):
        """Blesses your chat with a cute koala picture!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/koala') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title='🐨 Koala!', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def wink(self, ctx):
        """😉"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/animu/wink') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title=f'{ctx.message.author.name} winks 😉', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def pat(self, ctx, user: discord.Member = None):
        """Pat someone or yourself."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/animu/pat') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title=f'{ctx.message.author.name} pats {f"themselves. 😔" if user is None else f"{user.name} <:angery:545969728527663114>"}', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """Hug someone or yourself."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/animu/hug') as r:
                res = await r.json()
                imgUrl = res['link']
        embed = discord.Embed(title=f'{ctx.message.author.name} hugs {f"themselves. 😔" if user is None else f"{user.name} <:angery:545969728527663114>"}', color=get_config().COLOR).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def avatar(self, ctx, user : discord.Member = None):
        """Gets a user's avatar. Returns invoker's avatar if no user is specified."""
        embed = discord.Embed(title=f"{ctx.message.author.name if user is None else user.avatar_url}'s avatar.", color=get_config().COLOR).set_image(url=ctx.message.author.avatar_url if user is None else user.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Image(bot))
