from __future__ import annotations

from typing import Optional

import aiohttp
import discord
from classes.enums.animals import Animal
from discord import app_commands
from discord.ext import commands


class Image(commands.Cog):
    """
    Various image-related commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="avatar", description="Gets a user's avatar")
    @app_commands.describe(user="(Optional) The user you want the avatar for")
    async def avatar_command(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member],
    ) -> None:
        if user is None:
            user = interaction.user
        embed = discord.Embed(
            title=f"{user}'s avatar.",
            color=self.bot.config.color,
        ).set_image(url=user.avatar)
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="animal", description="Sends a random animal image")
    @app_commands.describe(animal="Name of the animal")
    async def animal_command(
        self,
        interaction: discord.Interaction,
        animal: Animal,
    ) -> None:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                f"https://some-random-api.ml/animal/{animal.name}",
            ) as r:
                res = await r.json()

        embed = discord.Embed(
            title=animal.icon,
            description=f"**{animal.display_name} Fact:**\n{res['fact']}",
            color=self.bot.config.color,
        ).set_image(url=res["image"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="wink", description="😉")
    async def wink_command(self, interaction: discord.Interaction) -> None:
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/wink") as r:
                res = await r.json()
                imgUrl = res["link"]

        embed = discord.Embed(
            title=f"{interaction.user} winks 😉",
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="pat", description="Give someone (or yourself) a pat")
    async def pat_command(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member],
    ) -> None:
        if user is None:
            user = interaction.user

        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/pat") as r:
                res = await r.json()

        embed = discord.Embed(
            title=f'{user} pats {f"themselves. 😔" if user is None else f"{user} <:angery:545969728527663114>"}',
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="hug", description="Give someone (or yourself) a hug")
    async def hug_command(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member],
    ) -> None:
        if user is None:
            user = interaction.user

        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/hug") as r:
                res = await r.json()

        embed = discord.Embed(
            title=f'{user} hugs {f"themselves. 😔" if user is None else f"{user} <:angery:545969728527663114>"}',
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Image(bot))
