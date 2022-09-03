import discord
from discord.ext import commands
import aiohttp
from classes.enums.animals import Animal
from commons import helpers


class Image(commands.Cog):
    """
    Various image-related commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=Animal.list())
    @helpers.docstring_parameter(" ".join(Animal.list()))
    async def animal(self, ctx):
        """Sends a random animal image and fact.\nChoose one via the following aliases:\n``{0}``"""
        if ctx.invoked_with == "animal":
            return
        currAnimal = Animal.from_name(ctx.invoked_with)
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                f"https://some-random-api.ml/animal/{currAnimal.name}"
            ) as r:
                res = await r.json()
                imgUrl = res["image"]
                fact = res["fact"]
        embed = discord.Embed(
            title=currAnimal.icon,
            description=f"**{currAnimal.display_name} Fact:**\n{fact}",
            color=self.bot.config.color,
        ).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def wink(self, ctx):
        """😉"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/wink") as r:
                res = await r.json()
                imgUrl = res["link"]
        embed = discord.Embed(
            title=f"{ctx.author.name} winks 😉", color=self.bot.config.color
        ).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def pat(self, ctx, user: discord.Member = None):
        """Pat someone (or yourself)."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/pat") as r:
                res = await r.json()
                imgUrl = res["link"]
        embed = discord.Embed(
            title=f'{ctx.author.name} pats {f"themselves. 😔" if user is None else f"{user.name} <:angery:545969728527663114>"}',
            color=self.bot.config.color,
        ).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """Hug someone (or yourself)."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/hug") as r:
                res = await r.json()
                imgUrl = res["link"]
        embed = discord.Embed(
            title=f'{ctx.author.name} hugs {f"themselves. 😔" if user is None else f"{user.name} <:angery:545969728527663114>"}',
            color=self.bot.config.color,
        ).set_image(url=imgUrl)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """Gets a user's avatar. Returns invoker's avatar if no user is specified."""
        embed = discord.Embed(
            title=f"{ctx.author.name if user is None else user.name}'s avatar.",
            color=self.bot.config.color,
        ).set_image(url=ctx.author.avatar_url if user is None else user.avatar_url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Image(bot))
