###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
import discord
from classes.cog import MetadataCog
from discord import app_commands
from discord.ext import commands
from models.enums.animals import Animal

if TYPE_CHECKING:
    from classes.bot import Sunny


class Image(MetadataCog):
    """
    Various image-related commands.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="avatar", description="Gets a user's avatar")
    @app_commands.describe(user="(Optional) The user you want the avatar for")
    async def avatar_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None,
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
    @app_commands.command(name="wink", description="Wink")
    async def wink_command(self, interaction: discord.Interaction) -> None:
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/wink") as r:
                res = await r.json()

        embed = discord.Embed(
            title=f"{interaction.user} winks 😉",
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="pat", description="Give someone a pat")
    @app_commands.describe(user="User to pat")
    async def pat_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None,
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
    @app_commands.command(name="hug", description="Give someone a hug")
    @app_commands.describe(user="User to hug")
    async def hug_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None,
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


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Image(bot))
